# hold a single database connection

import threading, sqlite, math, time

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
      print 'Slow SQL:', elapsed, args, kwargs
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
  
class IAAvg:
  def __init__(self):
    self.reset()

  def reset(self):
    self.last = None
    self.n = 0
    self.sx = 0

  def step(self, x):
    x = float(x)
    if self.last == None:
      self.last = x
    else:
      assert x > self.last
      x, self.last = x - self.last, x
      self.n += 1
      self.sx += x

  def finalize(self):
    if self.n == 0:
      return 0
    else:
      val = self.sx / self.n
      self.reset()
      return str(val)
  
class IAStdDev:
  def __init__(self):
    self.reset()

  def reset(self):
    self.last = None
    self.n = 0
    self.sx = 0
    self.sxx = 0

  def step(self, x):
    x = float(x)
    if self.last == None:
      self.last = x
    else:
      assert x > self.last
      x, self.last = x - self.last, x
      self.n += 1
      self.sx += x
      self.sxx += x * x

  def finalize(self):
    if self.n == 0:
      return 0
    else:
      val = math.sqrt(
        (self.n * self.sxx - self.sx * self.sx) / self.n / self.n)
      self.reset()
      return str(val)
  
if __name__ == '__main__':
  db.db.create_aggregate('stddev', 1, StdDev)
  db.db.create_aggregate('inter_arrival_avg', 1, IAAvg)
  db.db.create_aggregate('inter_arrival_stddev', 1, IAStdDev)
  c = db.db.cursor()
  c.execute("""select feed_title,
  inter_arrival_avg(julianday(item_created)),
  inter_arrival_stddev(julianday(item_created))
  from fm_feeds, fm_items where feed_uid=item_feed_uid
  group by feed_title
  order by item_created""")
  import pprint
  pprint.pprint(c.fetchall())
  import code
  code.interact(local=locals())
