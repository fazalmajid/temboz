# hold a single database connection

import sys, threading, sqlite, math, time

class PseudoCursor:
  def __init__(self, db):
    self.db = db
    self.db.lock.acquire()
    self.c = self.db.db.cursor()
  def __del__(self):
    self.db.lock.release()
  def __getattr__(self, name):
    return getattr(self.c, name, None)
  def execute(self, *args, **kwargs):
    before = time.time()
    result = self.c.execute(*args, **kwargs)
    elapsed = time.time() - before
    if elapsed > 5.0:
      print >> sys.stderr, 'Slow SQL:', elapsed, args, kwargs
    return result

class PseudoDB:
  def __init__(self):
    self.lock = threading.RLock()
    self.db = sqlite.connect('rss.db', mode=077)
    self.sqlite_last_insert_rowid = self.db.db.sqlite_last_insert_rowid
    self.c = self.db.cursor()
  def cursor(self):
    return PseudoCursor(self)
  def commit(self, *args, **kwargs):
    self.db.commit(*args, **kwargs)
  def rollback(self, *args, **kwargs):
    self.db.rollback(*args, **kwargs)
    
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
