import md5, time, feedparser, normalize

import socket
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

def update_feed(db, feed_uid, feed_xml, feed_etag, feed_modified):
  print feed_xml
  if not feed_etag:
    feed_etag = None
  if not feed_modified:
    feed_modified = None
  else:
    feed_modified = eval(feed_modified)
    assert type(feed_modified) == tuple, repr(feed_modified)
  try:
    f = feedparser.parse(feed_xml, etag=feed_etag, modified=feed_modified)
  except socket.timeout:
    f = {'channel': {}, 'items': []}
  c2 = db.cursor()
  # check for errors - HTTP code 304 means no change
  if 'title' not in f['channel'] and 'link' not in f['channel'] and \
         ('status' not in f or f['status'] not in [304]):
    # error or timeout - increment error count
    print '!' * 72
    print f
    print '!' * 72
    c2.execute("""update fm_feeds set feed_errors = feed_errors + 1
    where feed_uid=%d""" % feed_uid)
  else:
    # no error - reset etag and/or modified date and error count
    stmt = 'update fm_feeds set feed_errors=0'
    if 'etag' in f:
      stmt += ", feed_etag='%s'" % escape(f['etag'])
    else:
      stmt += ", feed_etag=NULL"
    if 'modified' in f:
      stmt += ", feed_modified='%s'" % escape(repr(f['modified']))
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
  c1 = db.cursor()
  c1.execute("""select feed_uid, feed_xml, feed_etag, feed_modified
  from fm_feeds""")
  for feed_uid, feed_xml, feed_etag, feed_modified in c1:
  #for feed_uid, feed_xml, feed_etag, feed_modified in c1.fetchall()[:2]:
    update_feed(db, feed_uid, feed_xml, feed_etag, feed_modified)
  db.commit()
  c1.close()
