import sys, os, threading, queue
sys.path.append('.')
os.chdir('..')
import normalize
from singleton import db

num_workers = 64

in_q = queue.Queue()
out_q = queue.Queue()
class Worker(threading.Thread):
  def run(self):
    while True:
      uid, url = in_q.get()
      if uid is None:
        out_q.put((None, None, None))
        return
      new_url = normalize.dereference(url)
      if url != new_url:
        out_q.put((uid, url, new_url))

workers = []
for i in range(num_workers):
  workers.append(Worker())
  workers[-1].setDaemon(True)
  workers[-1].start()

c = db.cursor()
c.execute("""select item_uid, item_link
from fm_items
where item_rating>0
order by item_uid""")
list(map(in_q.put, c))
list(map(in_q.put, [(None, None)] * num_workers))


while True:
  uid, url, new_url = out_q.get()
  if uid is None and url is None and new_url is None:
    num_workers -= 1
    if num_workers == 0:
      db.commit()
      sys.exit(0)
    continue
  print(uid, url)
  print('\t==>', new_url)
  c.execute('update fm_items set item_link=? where item_uid=?',
            [new_url, uid])
