# hold a single database connection

import threading, sqlite

class PseudoCursor:
  def __init__(self, db):
    self.db = db
    self.db.lock.acquire()
    self.c = self.db.db.cursor()
  def __del__(self):
    self.db.lock.release()
  def __getattr__(self, name):
    return getattr(self.c, name, None)

class PseudoDB:
  def __init__(self):
    self.lock = threading.RLock()
    self.db = sqlite.connect('rss.db', mode=077)
    self.c = self.db.cursor()
  def cursor(self):
    return PseudoCursor(self)
  def commit(self, *args, **kwargs):
    self.db.commit(*args, **kwargs)
  def rollback(self, *args, **kwargs):
    self.db.rollback(*args, **kwargs)
    
db = PseudoDB()
