import md5, time, threading, socket, Queue, signal
import param, feedparser, normalize

socket.setdefaulttimeout(10)

def escape(str):
  return str.replace("'", "''")

def add_feed(feed_xml):
  from singleton import db
  c = db.cursor()
  f = feedparser.parse(feed_xml)
  feed = {
    'xmlUrl': f['link'],
    'htmlUrl': f['channel']['link'],
    'etag': f['etag'],
    'title': f['channel']['title']
    }
  try:
    c.execute("""insert into fm_feeds
    (feed_xml, feed_etag, feed_html, feed_title, feed_desc) values
    ('%(xmlUrl)s', '%(etag)s', '%(htmlUrl)s', '%(title)s',
    '%(desc)s')""" % feed)
    feed_uid = db.db.sqlite_last_insert_rowid()
    process_parsed_feed(f, c, feed_uid)
    db.commit()
  except sqlite.IntegrityError, e:
    if 'feed_xml' not in str(e):
      raise
    else:
      # duplicate attempt
      pass
  c.close()

class FeedWorker(threading.Thread):
  def __init__(self, id, in_q, out_q):
    threading.Thread.__init__(self)
    self.id = id
    self.in_q = in_q
    self.out_q = out_q
  def run(self):
    try:
      while True:
        feed = self.in_q.get()
        if not feed: return
        f = self.fetch_feed(*feed)
        self.out_q.put((f,) + feed)
    finally:
      self.out_q.put(None)
  def fetch_feed(self, feed_uid, feed_xml, feed_etag, feed_modified):
    print self.id, feed_xml
    return fetch_feed(feed_uid, feed_xml, feed_etag, feed_modified)

def fetch_feed(feed_uid, feed_xml, feed_etag, feed_modified):
  if not feed_etag:
    feed_etag = None
  if not feed_modified:
    feed_modified = None
  try:
    f = feedparser.parse(feed_xml, etag=feed_etag, modified=feed_modified)
  except socket.timeout:
    if param.debug:
      print 'EEEEE error fetching feed', feed_xml
    f = {'channel': {}, 'items': []}
  return f

def update_feed(db, f, feed_uid, feed_xml, feed_etag, feed_modified):
  print feed_xml
  c2 = db.cursor()
  # check for errors - HTTP code 304 means no change
  if 'title' not in f['channel'] and 'link' not in f['channel'] and \
         ('status' not in f or f['status'] not in [304]):
    # error or timeout - increment error count
    c2.execute("""update fm_feeds set feed_errors = feed_errors + 1
    where feed_uid=%d""" % feed_uid)
  else:
    # no error - reset etag and/or modified date and error count
    stmt = 'update fm_feeds set feed_errors=0'
    if 'etag' in f and f['etag']:
      stmt += ", feed_etag='%s'" % escape(f['etag'])
    else:
      stmt += ", feed_etag=NULL"
    if 'modified' in f and f['modified']:
      stmt += ", feed_modified=julianday(%f, 'unixepoch')" \
              % time.mktime(f['modified'])
    else:
      stmt += ", feed_modified=NULL"
    stmt += " where feed_uid=%d" % feed_uid
    c2.execute(stmt)
  process_parsed_feed(f, c2, feed_uid)

def process_parsed_feed(f, c, feed_uid):
  # the Radio convention is reverse chronological order
  f['items'].reverse()
  for item in f['items']:
    normalize.normalize(item, f)
    title   = item['title']
    link    = item['link']
    creator = item['creator']
    created = item['date']
    modified = item['modified']
    if modified:
      modified = "julianday('%s')" % escape(modified)
    else:
      modified = 'NULL'
    content = item['content']
    # check if the item already exists, using the permalink as key
    c.execute("""select item_uid, item_loaded, item_created, item_modified,
               item_viewed, item_md5hex, item_title, item_content, item_creator
               from fm_items
               where item_feed_uid=%d and item_link='%s'""" \
               % (feed_uid, escape(link)))
    l = c.fetchall()
    import code
    from sys import exit
    ###if 'modified' in item:
    ###  code.interact(local=locals())
    # permalink doesn't exist yet, insert it
    if not l:
      sql = """insert into fm_items (item_feed_uid,
      item_created,   item_modified, item_viewed, item_link, item_md5hex,
      item_title, item_content, item_creator) values (%d,
      julianday('%s'), %s,          NULL,        '%s',      '%s',
      '%s',       '%s',         '%s')""" % \
      (feed_uid, escape(created), modified, escape(link),
       md5.new(content).hexdigest(),
       escape(title),
       escape(content),
       escape(creator))
      c.execute(sql)
      print ' ' * 4, title
    # permalink already exists, this is a change
    else:
      assert len(l) == 1
      (item_uid, item_loaded, item_created, item_modified,
       item_viewed, item_md5hex, item_title, item_content, item_creator) = l[0]

def update():
  from singleton import db
  # create worker threads and the queues used to communicate with them
  work_q = Queue.Queue()
  process_q = Queue.Queue()
  workers = []
  for i in range(param.feed_concurrency):
    workers.append(FeedWorker(i + 1, work_q, process_q))
    workers[-1].start()
  # assign work
  c1 = db.cursor()
  c1.execute("""select feed_uid, feed_xml, feed_etag,
  strftime('%s', feed_modified)
  from fm_feeds""")
  for feed_uid, feed_xml, feed_etag, feed_modified in c1:
    if feed_modified:
      feed_modified = float(feed_modified)
      feed_modified = time.localtime(feed_modified)
    else:
      feed_modified = None
    work_q.put((feed_uid, feed_xml, feed_etag, feed_modified))
  # None is an indication to workers to stop
  for i in range(param.feed_concurrency):
    work_q.put(None)
  workers_left = param.feed_concurrency
  while workers_left > 0:
    feed_info = process_q.get()
    # exited worker
    if not feed_info:
      workers_left -= 1
    else:
      update_feed(db, *feed_info)
  db.commit()
  c1.close()
