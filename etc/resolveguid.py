import sys, os
sys.path.append(os.getcwd())
sys.path.append('..')
from singleton import db
c = db.cursor()

def escape(str):
  return str.replace("'", "''")

c.execute("""select item_uid, item_link, item_feed_uid, item_guid
from fm_items
where item_link != item_guid""")
l = c.fetchall()
for uid, link, feed, guid in l:
  c.execute("""select item_uid from fm_items
  where item_link='%s' and item_feed_uid=%s""" % (link, feed))
  ll = c.fetchall()
  ll = [x[0] for x in ll]
  assert uid in ll
  if len(ll) > 2:
    print('could not resolve link', link, end=' ')
    print('more than 2 instances:', ', '.join(map(str, ll)))
    continue
  if len(ll) < 2: continue
  ll.remove(uid)
  old_uid = ll[0]
  c.execute("""delete from fm_items where item_uid=%s""" % uid)
  c.execute("""update fm_items set item_guid='%s' where item_uid=%s"""
            % (escape(guid), old_uid))
  db.commit()

