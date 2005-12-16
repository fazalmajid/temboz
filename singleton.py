# SQLite 2.x will throw an OperationalError rather than block if a reader and
# a writer thread collide. This module wraps a SQLite object with a Python
# mutex to prevent this from happening inside Temboz

import sys, threading, math, time, param

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
  def execute(self, *args, **kwargs):
    before = time.time()
    result = self.c.execute(*args, **kwargs)
    elapsed = time.time() - before
    if elapsed > 5.0:
      print >> param.log, 'Slow SQL:', elapsed, args, kwargs
    return result
  def sqlite_last_insert_rowid(self):
    return self.db.db.db.sqlite_last_insert_rowid()
  lastrowid = property(sqlite_last_insert_rowid)

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
  def __getattr__(self, name):
    t = threading.currentThread()
    db = getattr(t, '__singleton_db', None)
    if not db:
      from pysqlite2 import dbapi2 as sqlite
      db = sqlite.connect('rss.db')
      setattr(t, '__singleton_db', db)
    del t
    return getattr(db, name)

# name of the command-line executable for SQLite
sqlite_cli = 'sqlite'

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
