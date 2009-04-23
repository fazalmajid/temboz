# SQLite 2.x will throw an OperationalError rather than block if a reader and
# a writer thread collide. This module wraps a SQLite object with a Python
# mutex to prevent this from happening inside Temboz

import sys, thread, threading, signal, math, time
import param

try:
  from sqlite3 import dbapi2 as sqlite
except ImportError:
  from pysqlite2 import dbapi2 as sqlite
# XXX need to use PATH instead
sqlite_cli = '/usr/local/bin/sqlite3'

########################################################################
# custom aggregate function to calculate the exponentially decaying SNR

class SNR:
  """Calculates an exponentially decaying signal to noise ratio"""
  def __init__(self):
    self.reset()

  def reset(self):
    # it doesn't matter which date we use as a reference, as it just ends
    # up as a scaling factor on numerator and denominator
    # picking something close to localtime is preferrable so the exponents
    # stay manageable, julianday('1970-01-01 00:00:00') = 2440587.5
    self.ref_date = time.time() / 86400.0 + 2440587.5
    # this is the decaying sum of all except filtered
    self.sum_rated = 0.0
    # this is the decaying sum of all interesting
    self.sum_good = 0.0

  def step(self, rating, date, decay):
    """The aggregate function takes the following parameters:
    status: value of item_rating
    date:   value of item_created
    decay:  half-life to use, in days
    """
    # articles older than param.garbage_items cannot be counted towards
    # the SNR, as the uninteresting ones have been purged and thus skew
    # the metric towards 100%
    if self.ref_date - date < param.garbage_items:
      # by convention, 0 means do not decay (i.e. infinite half-life)
      if decay == 0:
        decay = 1
      else:
        decay = .5 ** ((self.ref_date - date) / decay)
      self.sum_rated += decay * int(rating not in [0, -2])
      self.sum_good += decay * int(rating == 1)

  def finalize(self):
    if self.sum_rated == 0:
      return 0
    else:
      return self.sum_good / self.sum_rated
  
# support classes for SQLite3, essentially to catch the OperationalError
# exceptions thrown when two writers collide

class PseudoCursor3(object):
  def __init__(self, db):
    self.c = db.cursor()
  def __str__(self):
    return '<SQLite3 Cursor wrapper>'
  def __repr__(self):
    return self.__str__()
  def __iter__(self):
    return iter(self.c)
  def __getattr__(self, name):
    return getattr(self.c, name, None)
  def execute(self, *args, **kwargs):
    global db
    # SQLite3 can deadlock when multiple writers collide, so we use a lock to
    # prevent this from happening
    if args[0].split()[0].lower() in ['insert', 'update', 'delete'] \
           and not self.locked:
      db.acquire()
    before = time.time()
    if param.debug:
      print >> param.log, thread.get_ident(), time.time(), args
    backoff = 0.1
    done = False
    while not done:
      try:
        result = self.c.execute(*args, **kwargs)
        done = True
      except sqlite.OperationalError, e:
        if param.debug:
          print >> param.log, thread.get_ident(), time.time(), str(e),
          print >> param.log, 'sleeping for', backoff
        time.sleep(backoff)
        backoff = min(backoff * 2, 5.0)
    elapsed = time.time() - before
    if param.debug:
      if elapsed > 5.0:
        print >> param.log, 'Slow SQL:', elapsed, args, kwargs
      print >> param.log, thread.get_ident(), time.time(), 'done'
    return result

def commit_wrapper(method):
  """Provide locking error recovery for commit/rollback"""
  global db
  backoff = 0.1
  done = False
  while not done:
    try:
      method()
      db.release()
      if param.debug:
        print >> param.log, thread.get_ident(), time.time(), 'commit'
      done = True
    except sqlite.OperationalError, e:
      if param.debug:
        print >> param.log, thread.get_ident(), time.time(), str(e),
        print >> param.log, 'sleeping for', backoff
      time.sleep(backoff)
      backoff = min(backoff * 2, 5.0)

class SQLite3Factory:
  """SQLite 3.x has a different, improved concurrency model, but it
has also tightened checking. Among other things, database objects
may not be shared between threads, apparently due to bugs in some
RedHat Linux threading library implementations:
    http://www.hwaci.com/sw/sqlite/faq.html#q8

Thus for SQLite 3.x, singleton.db acts like an implicit factory
object returning a new connection for each call. We cache the
database connection objects in the threading.Thread object (not
officially supported, but works well enough) so commits can be
associated with the corresponding cursor call.
"""
  lock = threading.Lock()
  def acquire(self):
    t = threading.currentThread()
    if not getattr(t, '__singleton_locked', False):
      if param.debug:
        print >> param.log, thread.get_ident(), time.time(), 'ACQUIRE'
      self.lock.acquire()
      setattr(t, '__singleton_locked', True)
      if param.debug:
        print >> param.log, thread.get_ident(), time.time(), 'DONE'
    del t
  def release(self):
    t = threading.currentThread()
    if getattr(t, '__singleton_locked', False):
      if param.debug:
        print >> param.log, thread.get_ident(), time.time(), 'RELEASE'
      self.lock.release()
      setattr(t, '__singleton_locked', False)
      if param.debug:
        print >> param.log, thread.get_ident(), time.time(), 'DONE'
    del t
  
  def __getattr__(self, name):
    t = threading.currentThread()
    db = getattr(t, '__singleton_db', None)
    if not db:
      db = sqlite.connect('rss.db')
      setattr(t, '__singleton_db', db)
      setattr(t, '__singleton_locked', False)
      db.create_aggregate('snr_decay', 3, SNR)
    del t
    if name == 'cursor':
      return lambda: PseudoCursor3(db)
    elif name in ['commit', 'rollback']:
      return lambda: commit_wrapper(getattr(db, name))
    else:
      return getattr(db, name)

class PseudoDB:
  def __init__(self):
    self.lock = threading.RLock()
    self.sqlite_last_insert_rowid = None        
    # try PySQLite2/SQLite3 first, fall back to PySQLite 1.0/SQLite2
    self.db = sqlite.connect('rss.db')
    self.db.create_aggregate('snr_decay', 3, SNR)
    try:
      # sanity checking
      c = self.db.cursor()
      c.execute('select count(*) from fm_feeds')
      l = c.fetchone()
      # black magic here, see this article for more info on the technique:
      #     http://www.majid.info/mylos/weblog/2002/09/07-1.html
      self.__class__ = SQLite3Factory
    except sqlite.DatabaseError, e:
      if str(e) == 'file is encrypted or is not a database':
        print >> param.log, 'NOTICE: rss.db uses the SQLite 2.x format'
        print >> param.log, 'SQLite 2.x is no longer supported by Temboz'
        print >> param.log, 'To upgrade to 3.x, see instructions at:'
        print >> param.log, \
              '\thttp://www.temboz.com/temboz/wiki?p=UpgradingSqlite'
        raise
      if 'no such table' in str(e):
        print >> param.log, 'WARNING: empty database, populating...',
        self.populate_tables()
        print >> param.log, 'done.'
    self.c = self.db.cursor()
  def cursor(self):
    return PseudoCursor3(self.db)
  def commit(self, *args, **kwargs):
    self.db.commit(*args, **kwargs)
  def rollback(self, *args, **kwargs):
    self.db.rollback(*args, **kwargs)
  def populate_tables(self):
    import os
    os.system('sqlite3 rss.db < ddl.sql')
    
db = PseudoDB()

########################################################################
# upgrade data model on demand
c = db.cursor()
c.execute("select sql from sqlite_master where name='v_feeds'")
sql = c.fetchone()
if sql:
  c.execute("""drop view v_feeds""")
  c.execute("""drop view v_feed_stats""")
  sql = None

# SQLite3 offers ALTER TABLE ADD COLUMN but not SQLite 2, so we do it the
# hard way, which shouldn't be an issue for a small table like this
c.execute("select count(*) from sqlite_master where name='fm_feeds' and sql like '%feed_filter%'")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: upgrading table fm_feeds...',
  c.execute("""create table sop as select fm_feeds.*, 0 as feed_frequency, null as feed_auth, null as feed_filter from fm_feeds""")
  c.execute('drop table fm_feeds')
  c.execute("""create table fm_feeds (
	feed_uid	integer primary key,
	feed_xml	varchar(255) unique not null,
	feed_etag	varchar(255),
	feed_modified	varchar(255),
	feed_html	varchar(255) not null,
	feed_title	varchar(255),
	feed_desc	text,
	feed_errors	int default 0,
	feed_lang	varchar(2) default 'en',
	feed_private	int default 0,
	feed_dupcheck	int default 0,
	feed_oldest	timestamp,
	-- 0=active, 1=suspended
	feed_status	int default 0,
	-- 0=hourly, 1=daily, 2=weekly, 3=monthly
	feed_frequency	int default 0,
	feed_auth	varchar(255),
	feed_filter	text
)""")
  c.execute('insert into fm_feeds select * from sop')
  c.execute('drop table sop')
  db.commit()  
  print >> param.log, 'done.'

c.execute("""select count(*) from sqlite_master
where name='fm_rules' and sql like '%rule_type%'""")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: upgrading table fm_rules to add rule_type...',
  c.execute("""alter table fm_rules
  add column rule_type varchar(16) not null default 'python'""")
  db.commit()  
  print >> param.log, 'done.'

c.execute("""select count(*) from sqlite_master
where name='fm_rules' and sql like '%rule_feed%'""")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: upgrading table fm_rules to add rule_feed_uid...',
  c.execute("""alter table fm_rules
  add column rule_feed_uid integer""")
  db.commit()  
  print >> param.log, 'done.'

c.execute("""select count(*) from sqlite_master
where name='fm_items' and sql like '%item_rule_uid%'""")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: upgrading table fm_items to add item_rule_uid...',
  c.execute("""alter table fm_items add column item_rule_uid integer""")
  db.commit()  
  print >> param.log, 'done.'

c.execute("""select count(*) from sqlite_master
where name='fm_feeds' and sql like '%feed_exempt%'""")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: upgrading table fm_feeds to add feed_exempt...',
  c.execute("""alter table fm_feeds add column feed_exempt integer default 0""")
  db.commit()  
  print >> param.log, 'done.'

# we have to recreate this view each time as param.decay may have changed
c.execute("select sql from sqlite_master where name='v_feeds_snr'")
sql = c.fetchone()
if not sql:
  c.execute("""create view v_feeds_snr as
select feed_uid, feed_title, feed_html, feed_xml,
min(julianday('now') - item_modified) as last_modified,
sum(case when item_rating=1 then 1 else 0 end) as interesting,
sum(case when item_rating=0 then 1 else 0 end) as unread,
sum(case when item_rating=-1 then 1 else 0 end) as uninteresting,
sum(case when item_rating=-2 then 1 else 0 end) as filtered,
sum(1) as total,
snr_decay(item_rating, item_created, %d) as snr,
feed_status, feed_private, feed_exempt, feed_errors, feed_desc, feed_filter
from fm_feeds left outer join (
  select item_rating, item_feed_uid, item_created,
    ifnull(
      julianday(item_modified),
      julianday(item_created)
    ) as item_modified
  from fm_items
) on feed_uid=item_feed_uid
group by feed_uid, feed_title, feed_html, feed_xml""" %
          getattr(param, 'decay', 30))
  db.commit()  
