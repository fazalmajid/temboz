import sys, md5, time, threading, socket, Queue, signal, sqlite, os
import param, feedparser, normalize

socket.setdefaulttimeout(10)
feedparser.USER_AGENT = param.user_agent

def escape(str):
  return str.replace("'", "''")

class ParseError(Exception):
  pass
class FeedAlreadyExists(Exception):
  pass
class UnknownError(Exception):
  pass

def add_feed(feed_xml):
  """Try to add a feed. Returns a tuple (feed_uid, num_added, num_filtered)
  -1: unknown error
  0: feed added normally
  1: feed added via autodiscovery
  2: feed not added, already present
  3: feed not added, connection or parse error"""
  from singleton import db
  c = db.cursor()
  try:
    f = feedparser.parse(feed_xml)
    if not f.feed:
      raise ParseError
    normalize.normalize_feed(f)
    feed = {
      'xmlUrl': f['url'],
      'htmlUrl': str(f.feed['link']),
      'etag': f['etag'],
      'title': f.feed['title'].encode('ascii', 'xmlcharrefreplace'),
      'desc': f.feed['description'].encode('ascii', 'xmlcharrefreplace')
      }
    for key, value in feed.items():
      if type(value) == str:
        feed[key] = escape(value)
    try:
      c.execute("""insert into fm_feeds
      (feed_xml, feed_etag, feed_html, feed_title, feed_desc) values
      ('%(xmlUrl)s', '%(etag)s', '%(htmlUrl)s', '%(title)s',
      '%(desc)s')""" % feed)
      feed_uid = db.sqlite_last_insert_rowid()
      num_added, num_filtered = process_parsed_feed(f, c, feed_uid)
      db.commit()
      return (feed_uid, num_added, num_filtered)
    except sqlite.IntegrityError, e:
      if 'feed_xml' in str(e):
        db.rollback()
        raise FeedAlreadyExists
      else:
        db.rollback()
        raise UnknownError(str(e))
  finally:
    c.close()

def update_feed_xml(feed_uid, feed_xml):
  """Update a feed URL and fetch the feed. Returns the number of new items"""
  feed_uid = int(feed_uid)

  f = feedparser.parse(feed_xml)
  if not f.feed:
    raise ParseError
  normalize.normalize_feed(f)

  from singleton import db
  c = db.cursor()
  clear_errors(db, c, feed_uid, f)
  try:
    try:
      c.execute("""update fm_feeds set feed_xml='%s', feed_html='%s'
      where feed_uid=%d""" \
                % (escape(feed_xml), escape(str(f.feed['link'])), feed_uid))
    except sqlite.IntegrityError, e:
      if 'feed_xml' in str(e):
        db.rollback()
        raise FeedAlreadyExists
      else:
        db.rollback()
        raise UnknownError(str(e))
    num_added = process_parsed_feed(f, c, feed_uid)
    db.commit()
    return num_added
  finally:
    c.close()

def update_feed_title(feed_uid, feed_title):
  """Update a feed title"""
  feed_uid = int(feed_uid)

  from singleton import db
  c = db.cursor()
  try:
    c.execute("""update fm_feeds set feed_title='%s' where feed_uid=%d""" \
              % (escape(feed_title), feed_uid))
    db.commit()
  finally:
    c.close()

def catch_up(feed_uid):
  feed_uid = int(feed_uid)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("""update fm_items set item_rating=-1
    where item_feed_uid=%d and item_rating=0""" % feed_uid)
    db.commit()
  finally:
    c.close()

def set_status(feed_uid, status):
  feed_uid = int(feed_uid)
  status = int(status)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("""update fm_feeds set feed_status=%d where feed_uid=%d""" \
              % (status, feed_uid))
    db.commit()
  finally:
    c.close()

class FeedWorker(threading.Thread):
  def __init__(self, id, in_q, out_q):
    threading.Thread.__init__(self)
    self.id = id
    self.in_q = in_q
    self.out_q = out_q
    # we need to do this so temboz --refresh honors Ctrl-C
    self.setDaemon(True)
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

def increment_errors(db, c, feed_uid):
  """Increment the error counter, and suspend the feed if the threshold is
  reached"""
  c.execute('update fm_feeds set feed_errors=feed_errors+1 where feed_uid=%d' \
            % feed_uid)
  c.execute("""select feed_errors, feed_title
  from fm_feeds where feed_uid=%d""" % feed_uid)
  errors, feed_title = c.fetchone()
  max_errors = getattr(param, 'max_errors', 100)
  if max_errors != -1 and errors > max_errors:
    print 'EEEEE too many errors, suspending feed', feed_title
    c.execute('update fm_feeds set feed_status = 1 where feed_uid=%d' \
              % feed_uid)

def clear_errors(db, c, feed_uid, f):
  'On successful feed parse, reset etag and/or modified date and error count'
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
  c.execute(stmt)

def update_feed(db, c, f, feed_uid, feed_xml, feed_etag, feed_modified):
  print feed_xml
  # check for errors - HTTP code 304 means no change
  if 'title' not in f.feed and 'link' not in f.feed and \
         ('status' not in f or f['status'] not in [304]):
    # error or timeout - increment error count
    increment_errors(db, c, feed_uid)
  else:
    # no error - reset etag and/or modified date and error count
    clear_errors(db, c, feed_uid, f)
  process_parsed_feed(f, c, feed_uid)

# shades of LISP...
def curry(fn, obj):
  return lambda *args: fn(obj, *args)

# obj can be a string, list or dictionary
def any(obj, *words):
  for w in words:
    if w in obj:
      return True
  return False

def process_parsed_feed(f, c, feed_uid):
  """Insert the entries from a feedparser parsed feed f in the database using
the cursor c for feed feed_uid.
Returns a tuple (number of items added unread, number of filtered items)"""
  num_added = 0
  num_filtered = 0
  # the Radio convention is reverse chronological order
  f['items'].reverse()
  for item in f['items']:
    normalize.normalize(item, f)
    skip = 0
    filter_dict = {}
    for key in f.feed:
      try:
        filter_dict['feed_' + key] = f.feed[key]
      except KeyError:
        pass
    filter_dict.update(item)
    # convenient shortcut functions
    filter_dict['title_any_words'] = curry(any, item['title_words'])
    filter_dict['content_any_words'] = curry(any, item['content_words'])
    filter_dict['title_any'] = curry(any, item['title'])
    filter_dict['content_any'] = curry(any, item['content'])
    filter_dict['title_any_lc'] = curry(any, item['title_lc'])
    filter_dict['content_any_lc'] = curry(any, item['content_lc'])
    # evaluate the rules
    for rule in rules:
      try:
        skip = eval(rule, filter_dict)
        if skip:
          break
      except:
        e = sys.exc_info()[1]
        print e
    if skip:
      skip = -2
    title   = item['title']
    link    = item['link']
    guid    = item['id']
    author = item['author']
    created = item['created']
    modified = item['modified']
    if modified:
      modified = "julianday('%s')" % escape(modified)
    else:
      modified = 'NULL'
    content = item['content']
    # check if the item already exists, using the GUID as key
    c.execute("""select item_uid, item_link,
               item_loaded, item_created, item_modified,
               item_viewed, item_md5hex, item_title, item_content, item_creator
               from fm_items
               where item_feed_uid=%d and item_guid='%s'""" \
               % (feed_uid, escape(guid)))
    l = c.fetchall()
    # GUID doesn't exist yet, insert it
    if not l:
      sql = """insert into fm_items (item_feed_uid, item_guid,
      item_created,   item_modified, item_viewed, item_link, item_md5hex,
      item_title, item_content, item_creator, item_rating) values (%d, '%s',
      julianday('%s'), %s,          NULL,        '%s',      '%s',
      '%s',       '%s',         '%s', %d)""" % \
      (feed_uid, escape(guid), escape(created), modified, escape(link),
       md5.new(content).hexdigest(),
       escape(title),
       escape(content),
       escape(author),
       skip)
      c.execute(sql)
      if skip:
        num_filtered += 1
        print 'SKIP', title
      else:
        num_added += 1
        print ' ' * 4, title
    # GUID already exists, this is a change
    else:
      assert len(l) == 1
      (item_uid, item_link, item_loaded, item_created, item_modified,
       item_viewed, item_md5hex, item_title, item_content, item_creator) = l[0]
      # XXX update item here
  # update timestamp of the oldest item still in the feed file
  if 'oldest' in f and f['oldest'] != '9999-99-99 99:99:99':
    c.execute("""update fm_feeds
    set feed_oldest=julianday('%s')
    where feed_uid=%d""" % (f['oldest'], feed_uid))
  
  return (num_added, num_filtered)

def update():
  from singleton import db
  c = db.cursor()
  # refresh filtering rules
  load_rules()
  # garbage collection - see param.py
  # this is done only once a day between 3 and 4 AM as this is quite intensive
  # and could interfere with user activity
  if param.garbage_contents and time.localtime()[3] == 3:
    c.execute("""update fm_items
    set item_content=''
    where item_rating<0 and item_created < julianday('now')-%d""" %
               param.garbage_contents)
    db.commit()
    c.execute('vacuum')
    # we still hold the PseudoCursor lock, this is a good opportunity to backup
    try:
      os.mkdir('backups')
    except OSError:
      pass
    os.system(('sqlite rss.db .dump | %s > backups/daily_' \
               + time.strftime('%Y-%m-%d') + '%s') % param.backup_compressor)
    try:
      os.remove('backups/daily_'
                + time.strftime('%Y-%m-%d',
                                time.localtime(time.time()
                                               - 86400 * param.daily_backups))
                + param.backup_compressor[1])
    except OSError:
      pass
  # create worker threads and the queues used to communicate with them
  work_q = Queue.Queue()
  process_q = Queue.Queue()
  workers = []
  for i in range(param.feed_concurrency):
    workers.append(FeedWorker(i + 1, work_q, process_q))
    workers[-1].start()
  # assign work
  c.execute("""select feed_uid, feed_xml, feed_etag,
  strftime('%s', feed_modified)
  from fm_feeds where feed_status=0""")
  for feed_uid, feed_xml, feed_etag, feed_modified in c:
    if feed_modified:
      feed_modified = float(feed_modified)
      feed_modified = time.localtime(feed_modified)
    else:
      feed_modified = None
    work_q.put((feed_uid, feed_xml, feed_etag, feed_modified))
  # None is an indication for workers to stop
  for i in range(param.feed_concurrency):
    work_q.put(None)
  workers_left = param.feed_concurrency
  while workers_left > 0:
    feed_info = process_q.get()
    # exited worker
    if not feed_info:
      workers_left -= 1
    else:
      update_feed(db, c, *feed_info)
  db.commit()
  c.close()

class PeriodicUpdater(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.setDaemon(True)
  def run(self):
    while True:
      # XXX should wrap this in a try/except clause
      time.sleep(param.refresh_interval)
      print time.ctime(), '- refreshing feeds'
      update()

##############################################################################
#
rules = []
def load_rules():
  global rules
  rules = []
  from singleton import db
  c = db.cursor()
  try:
    c.execute("""select rule_uid, rule_text
    from fm_rules where rule_expires is null
    or rule_expires > julianday('now')""")
    for uid, rule in c:
      rules.append(compile(rule, 'rule' + `uid`, 'eval'))
  finally:
    c.close()

def update_rule(db, c, uid, expires, text, delete):
  if expires == 'never':
    expires = 'NULL'
  else:
    expires = "julianday('%s')" % expires
  # check syntax
  compile(text, 'web form', 'eval')
  if uid == 'new':
    c.execute("""insert into fm_rules (rule_expires, rule_text)
    values (%s, '%s')""" \
              % (expires, escape(text)))
  elif delete == 'on':
    c.execute("delete from fm_rules where rule_uid=%s" % uid)
  else:
    c.execute("""update fm_rules set rule_expires=%s, rule_text='%s'
    where rule_uid=%s""" % (expires, escape(text), uid))
  db.commit()
    
