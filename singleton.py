# SQLite 2.x will throw an OperationalError rather than block if a reader and
# a writer thread collide. This module wraps a SQLite object with a Python
# mutex to prevent this from happening inside Temboz

import sys, thread, threading, signal, math, time
import param

# name of the command-line executable for SQLite
sqlite_cli = 'sqlite'

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
    from pysqlite2 import dbapi2 as sqlite
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
  from pysqlite2 import dbapi2 as sqlite
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
  """SQLite 3.x has a different, improved concurrency model, but it has also
tightened checking. Among other things, database objects may not be shared
between threads, apparently due to bugs in some RedHat Linux threading
library implementations:
    http://www.hwaci.com/sw/sqlite/faq.html#q8

Thus for SQLite 3.x, singleton.db acts like an implicit factory object
returning a new connection for each call. We cache the database connection
objects in the threading.Thread object (not officially supported, but works
well enough) so commits can be associated with the corresponding cursor call.
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
      from pysqlite2 import dbapi2 as sqlite
      db = sqlite.connect('rss.db')
      setattr(t, '__singleton_db', db)
      setattr(t, '__singleton_locked', False)
    del t
    if name == 'cursor':
      return lambda: PseudoCursor3(db)
    elif name in ['commit', 'rollback']:
      return lambda: commit_wrapper(getattr(db, name))
    else:
      return getattr(db, name)

# support classes for SQLite2 to implement locking

class PseudoCursor(object):
  def __init__(self, db):
    self.db = db
    self.db.lock.acquire()
    self.c = self.db.db.cursor()
  def __del__(self):
    self.db.lock.release()
  def __str__(self):
    return '<SQLite Cursor wrapper>'
  def __repr__(self):
    return self.__str__()
  def __iter__(self):
    return iter(self.c)
  def __getattr__(self, name):
    return getattr(self.c, name, None)
  def __del__(self):
    del self.c
  def execute(self, *args, **kwargs):
    before = time.time()
    result = self.c.execute(*args, **kwargs)
    elapsed = time.time() - before
    if param.debug and elapsed > 5.0:
      print >> param.log, 'Slow SQL:', elapsed, args, kwargs
    return result
  def sqlite_last_insert_rowid(self):
    return self.db.db.db.sqlite_last_insert_rowid()
  lastrowid = property(sqlite_last_insert_rowid)

class PseudoDB:
  def __init__(self):
    global sqlite_cli
    self.lock = threading.RLock()
    self.sqlite_last_insert_rowid = None        
    # try PySQLite2/SQLite3 first, fall back to PySQLite 1.0/SQLite2
    try:
      from pysqlite2 import dbapi2 as sqlite
      self.db = sqlite.connect('rss.db')
      try:
        # sanity checking
        c = self.db.cursor()
        c.execute('select count(*) from fm_feeds')
        l = c.fetchone()
        # black magic here, see this article for more info on the technique:
        #     http://www.majid.info/mylos/weblog/2002/09/07-1.html
        self.__class__ = SQLite3Factory
        sqlite_cli = 'sqlite3'
      except sqlite.DatabaseError, e:
        if str(e) == 'file is encrypted or is not a database':
#           print >> param.log, 'NOTICE: rss.db uses the SQLite 2.x format'
#           print >> param.log, 'Upgrading to 3.x is recommended, see:'
#           print >> param.log, 'http://www.temboz.com/temboz/wiki?p=UpgradingSqlite'
          raise ImportError
        if 'no such table' in str(e):
          print >> param.log, 'WARNING: empty database, populating...',
          self.populate_tables()
          print >> param.log, 'done.'
    except ImportError:
      import sqlite
      self.db = sqlite.connect('rss.db', mode=077)
    self.c = self.db.cursor()
  def cursor(self):
    return PseudoCursor(self)
  def commit(self, *args, **kwargs):
    self.db.commit(*args, **kwargs)
  def rollback(self, *args, **kwargs):
    self.db.rollback(*args, **kwargs)
  def populate_tables(self):
    import os
    os.system('sqlite3 rss.db < ddl.sql')
    
db = PseudoDB()

# upgrade data model on demand
c = db.cursor()
c.execute("select count(*) from sqlite_master where name='v_feeds'")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: creating view v_feeds...',
  c.execute("""create view v_feeds as
  select feed_uid, feed_title, feed_html, feed_xml,
    min(last_modified) as last_modified,
    sum(case when item_rating=1 then cnt else 0 end) as interesting,
    sum(case when item_rating=0 then cnt else 0 end) as unread,
    sum(case when item_rating=-1 then cnt else 0 end) as uninteresting,
    sum(case when item_rating=-2 then cnt else 0 end) as filtered,
    sum(cnt) as total,
    feed_status, feed_private, feed_errors
  from fm_feeds left outer join (
    select item_rating, item_feed_uid, count(*) as cnt,
      julianday('now') - max(
      ifnull(
	julianday(item_modified),
	julianday(item_created)
      )
    ) as last_modified
    from fm_items
    group by item_rating, item_feed_uid
  ) on feed_uid=item_feed_uid
  group by feed_uid, feed_title, feed_html, feed_xml""")
  db.commit()  
  print >> param.log, 'done.'
c.execute("select count(*) from sqlite_master where name='v_feed_stats'")
if not c.fetchone()[0]:
  print >> param.log, 'WARNING: creating view v_feed_stats...',
  c.execute("""create view v_feed_stats as
  select feed_uid, feed_title, feed_html, feed_xml,
    last_modified,
    interesting, unread, uninteresting, filtered, total,
    interesting * 100.0 / (total - filtered - unread) as snr,
    feed_status, feed_private, feed_errors
  from v_feeds""")
  db.commit()  
  print >> param.log, 'done.'

########################################################################
# user-defined aggregate function to calculate the mean and standard
# deviation of inter-arrival times in a single pass on the database
# This will segfault with versions of PySQLite older than 0.5.1

class StdDev:
  def __init__(self):
    self.reset()

  def reset(self):
    self.n = 0
    self.sx = 0
    self.sxx = 0

  def step(self, x):
    x = float(x)
    self.n += 1
    self.sx += x
    self.sxx += x * x

  def finalize(self):
    val = math.sqrt((self.n * self.sxx - self.sx * self.sx) / self.n / self.n)
    self.reset()
    return str(val)
  
db.db.create_aggregate('stddev', 1, StdDev)
