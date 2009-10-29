import sys, md5, time, threading, socket, Queue, signal, os, re
import urllib2, urlparse, HTMLParser
import param, feedparser, normalize, util, transform, singleton, filters

sqlite = singleton.sqlite

socket.setdefaulttimeout(10)
feedparser.USER_AGENT = param.user_agent

class ParseError(Exception):
  pass
class AutodiscoveryParseError(Exception):
  pass
class FeedAlreadyExists(Exception):
  pass
class UnknownError(Exception):
  pass

ratings = [
  ('all',      'all',           'All articles',     'item_rating is not null'),
  ('unread',   'unread',        'Unread only',       'item_rating = 0'),
  ('down',     'uninteresting', 'Uninteresting only','item_rating = -1'),
  ('up',       'interesting',   'Interesting only',  'item_rating > 0'),
  ('filtered', 'filtered',      'Filtered only',     'item_rating = -2')
]
sorts = [
  ('created',  'article date',  'Article date',      'item_created DESC'),
  ('seen',     'cached date',   'Cached date',       'item_uid DESC'),
  ('snr',      'feed SNR',      'Feed SNR',          'snr DESC'),
]
sorts_dict = dict((sorts[i][0], i) for i in range(len(sorts)))

class AutoDiscoveryHandler(HTMLParser.HTMLParser):
  """Find RSS autodiscovery info, as specified in:
    http://diveintomark.org/archives/2002/05/30/rss_autodiscovery
  Cope even if the HTML document is not strictly XML compliant (as we do not
  use a SGML parser like htmllib.HTMLParser does"""
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.autodiscovery = {}
  def handle_starttag(self, tag, attrs):
    if tag == 'link':
      attrs = dict(attrs)
      if attrs.get('rel', '').strip().lower() != 'alternate':
        return
      if attrs.get('type') == 'application/rss+xml' and 'href' in attrs:
        self.autodiscovery['rss'] = attrs['href']
      if attrs.get('type') == 'application/atom+xml' and 'href' in attrs:
        self.autodiscovery['atom'] = attrs['href']
  def feed_url(self, page_url):
    page_data = urllib2.urlopen(page_url).read()
    self.feed(page_data)
    # Atom has cleaner semantics than RSS, so give it priority
    url = self.autodiscovery.get(
      'atom', self.autodiscovery.get('rss'))
    # the URL could be relative, if so fix it
    url = urlparse.urljoin(page_url, url)
    return url

def re_autodiscovery(url):
  autodiscovery_re = re.compile(
    '<link[^>]*rel="alternate"[^>]*'
    'application/(atom|rss)\\+xml[^>]*href="([^"]*)"')
  candidates = autodiscovery_re.findall(urllib2.urlopen(url).read())
  candidates.sort()
  return candidates

def add_feed(feed_xml):
  """Try to add a feed. Returns a tuple (feed_uid, num_added, num_filtered)"""
  from singleton import db
  c = db.cursor()
  try:
    # verify the feed
    f = feedparser.parse(feed_xml)
    # CVS versions of feedparser are not throwing exceptions as they should
    # see:
    # http://sourceforge.net/tracker/index.php?func=detail&aid=1379172&group_id=112328&atid=661937
    if not f.feed or ('link' not in f.feed or 'title' not in f.feed):
      # try autodiscovery
      try:
        feed_xml = AutoDiscoveryHandler().feed_url(feed_xml)
      except HTMLParser.HTMLParseError:
        # in desperate conditions, regexps ride to the rescue
        try:
          feed_xml = re_autodiscovery(feed_xml)[0][1]
        except:
          raise AutodiscoveryParseError
      if not feed_xml:
        raise ParseError
      f = feedparser.parse(feed_xml)
      if not f.feed:
        raise ParseError
    # we have a valid feed, normalize it
    normalize.normalize_feed(f)
    feed = {
      'xmlUrl': f['url'],
      'htmlUrl': str(f.feed['link']),
      'etag': f.get('etag'),
      'title': f.feed['title'].encode('ascii', 'xmlcharrefreplace'),
      'desc': f.feed['description'].encode('ascii', 'xmlcharrefreplace')
      }
    for key, value in feed.items():
      if type(value) == str:
        feed[key] = value
    filters.load_rules(db, c)
    try:
      c.execute("""insert into fm_feeds
      (feed_xml, feed_etag, feed_html, feed_title, feed_desc) values
      (:xmlUrl, :etag, :htmlUrl, :title, :desc)""", feed)
      feed_uid = c.lastrowid
      num_added, num_filtered = process_parsed_feed(db, c, f, feed_uid)
      db.commit()
      return feed_uid, feed['title'], num_added, num_filtered
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
      c.execute("update fm_feeds set feed_xml=?, feed_html=? where feed_uid=?",
                [feed_xml, str(f.feed['link']), feed_uid])
    except sqlite.IntegrityError, e:
      if 'feed_xml' in str(e):
        db.rollback()
        raise FeedAlreadyExists
      else:
        db.rollback()
        raise UnknownError(str(e))
    filters.load_rules(db, c)
    num_added = process_parsed_feed(db, c, f, feed_uid)
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
    c.execute("update fm_feeds set feed_title=? where feed_uid=?",
              [feed_title, feed_uid])
    db.commit()
  finally:
    c.close()

def update_feed_html(feed_uid, feed_html):
  """Update a feed HTML link"""
  feed_uid = int(feed_uid)

  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_html=? where feed_uid=?",
              [feed_html, feed_uid])
    db.commit()
  finally:
    c.close()

def update_feed_desc(feed_uid, feed_desc):
  """Update a feed desc"""
  feed_uid = int(feed_uid)

  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_desc=? where feed_uid=?",
              [feed_desc, feed_uid])
    db.commit()
  finally:
    c.close()

def update_feed_filter(feed_uid, feed_filter):
  """Update a feed desc"""
  feed_uid = int(feed_uid)
  feed_filter = feed_filter.strip()
  if feed_filter:
    # check syntax
    compile(filters.normalize_rule(feed_filter), 'web form', 'eval')
    val = feed_filter
  else:
    val = None
  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_filter=? where feed_uid=?",
              [val, feed_uid])
    db.commit()
    filters.invalidate()
  finally:
    c.close()

def update_feed_private(feed_uid, private):
  feed_uid = int(feed_uid)
  private = int(bool(private))
  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_private=? where feed_uid=?",
              [private, feed_uid])
    db.commit()
  finally:
    c.close()

def update_feed_exempt(feed_uid, exempt):
  feed_uid = int(feed_uid)
  exempt = int(bool(exempt))
  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_exempt=? where feed_uid=?",
              [exempt, feed_uid])
    if exempt:
      filters.exempt_feed_retroactive(db, c, feed_uid)
    db.commit()
  finally:
    c.close()

def update_feed_dupcheck(feed_uid, dupcheck):
  feed_uid = int(feed_uid)
  dupcheck = int(bool(dupcheck))
  # XXX run a dupcheck pass retroactively here if dupcheck == 1
  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_dupcheck=? where feed_uid=?",
              [dupcheck, feed_uid])
    db.commit()
  finally:
    c.close()

def update_item(item_uid, link, title, content):
  item_uid = int(item_uid)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("""update fm_items set item_link=?, item_title=?, item_content=?
    where item_uid=?""", [link, title, content, item_uid])
    db.commit()
  finally:
    c.close()

def title_url(feed_uid):
  feed_uid = int(feed_uid)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("select feed_title, feed_html from fm_feeds where feed_uid=?",
              [feed_uid])
    return c.fetchone()
  finally:
    c.close()

def catch_up(feed_uid):
  feed_uid = int(feed_uid)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("""update fm_items set item_rating=-1
    where item_feed_uid=? and item_rating=0""", [feed_uid])
    db.commit()
  finally:
    c.close()

def purge_reload(feed_uid):
  feed_uid = int(feed_uid)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("delete from fm_items where item_feed_uid=? and item_rating=0",
              [feed_uid])
    c.execute("""delete from fm_tags
    where exists (
      select item_uid from fm_items
      where item_uid=tag_item_uid and item_feed_uid=? and item_rating=0
    )""", [feed_uid])
    c.execute("""update fm_feeds set feed_modified=NULL, feed_etag=NULL
    where feed_uid=?""", [feed_uid])
    c.execute("select feed_xml from fm_feeds where feed_uid=?", [feed_uid])
    feed_xml = c.fetchone()[0]
    db.commit()
    f = feedparser.parse(feed_xml)
    if not f.feed:
      raise ParseError
    normalize.normalize_feed(f)
    clear_errors(db, c, feed_uid, f)
    filters.load_rules(db, c)
    num_added = process_parsed_feed(db, c, f, feed_uid)
    db.commit()
  finally:
    c.close()

def hard_purge(feed_uid):
  feed_uid = int(feed_uid)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("delete from fm_items where item_feed_uid=?", [feed_uid])
    c.execute("delete from fm_rules where rule_feed_uid=?", [feed_uid])
    c.execute("delete from fm_feeds where feed_uid=?", [feed_uid])
    db.commit()
  finally:
    c.close()
    filters.invalidate()

def set_status(feed_uid, status):
  feed_uid = int(feed_uid)
  status = int(status)
  from singleton import db
  c = db.cursor()
  try:
    c.execute("update fm_feeds set feed_status=? where feed_uid=?",
              [status, feed_uid])
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
        self.out_q.put((self.fetch_feed(*feed),) + feed)
    finally:
      self.out_q.put(None)
  def fetch_feed(self, feed_uid, feed_xml, feed_etag, feed_modified,
                 feed_dupcheck):
    print >> param.log, self.id, feed_xml
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
      print >> param.log, 'EEEEE error fetching feed', feed_xml
    f = {'channel': {}, 'items': []}
  return f

def increment_errors(db, c, feed_uid):
  """Increment the error counter, and suspend the feed if the threshold is
  reached
  """
  c.execute("update fm_feeds set feed_errors=feed_errors+1 where feed_uid=?",
            [feed_uid])
  c.execute("select feed_errors, feed_title from fm_feeds where feed_uid=?",
            [feed_uid])
  errors, feed_title = c.fetchone()
  max_errors = getattr(param, 'max_errors', 100)
  if max_errors != -1 and errors > max_errors:
    notification(db, c, feed_uid, 'Service notification',
                 'This feed was suspended because Temboz encountered '
                 + str(errors) + ' consecutive errors')
    print >> param.log, 'EEEEE too many errors, suspending feed', feed_title
    c.execute("update fm_feeds set feed_status = 1 where feed_uid=?",
              [feed_uid])

def clear_errors(db, c, feed_uid, f):
  'On successful feed parse, reset etag and/or modified date and error count'
  stmt = 'update fm_feeds set feed_errors=0'
  params = []
  if 'etag' in f and f['etag']:
    stmt += ", feed_etag=?"
    params.append(f['etag'])
  else:
    stmt += ", feed_etag=NULL"
  if 'modified' in f and f['modified']:
    stmt += ", feed_modified=julianday(?, 'unixepoch')"
    params.append(time.mktime(f['modified']))
  else:
    stmt += ", feed_modified=NULL"
  stmt += " where feed_uid=?"
  params.append(feed_uid)
  c.execute(stmt, params)

def update_feed(db, c, f, feed_uid, feed_xml, feed_etag, feed_modified,
                feed_dupcheck=None):
  print >> param.log, feed_xml
  # check for errors - HTTP code 304 means no change
  if 'title' not in f.feed and 'link' not in f.feed and \
         ('status' not in f or f['status'] not in [304]):
    # error or timeout - increment error count
    increment_errors(db, c, feed_uid)
  else:
    # no error - reset etag and/or modified date and error count
    clear_errors(db, c, feed_uid, f)
  try:
    process_parsed_feed(db, c, f, feed_uid, feed_dupcheck)
  except:
    util.print_stack(['c', 'f'])

def process_parsed_feed(db, c, f, feed_uid, feed_dupcheck=None, exempt=None):
  """Insert the entries from a feedparser parsed feed f in the database using
the cursor c for feed feed_uid.
Returns a tuple (number of items added unread, number of filtered items)"""
  num_added = 0
  num_filtered = 0
  filters.load_rules(db, c)
  # check if duplicate title checking is in effect
  if feed_dupcheck is None:
    c.execute("select feed_dupcheck from fm_feeds where feed_uid=?",
              [feed_uid])
    feed_dupcheck = bool(c.fetchone()[0])
  # check if the feed is exempt from filtering
  if exempt is None:
    c.execute("select feed_exempt from fm_feeds where feed_uid=?", [feed_uid])
    exempt = bool(c.fetchone()[0])
  # the Radio convention is reverse chronological order
  f['items'].reverse()
  for item in f['items']:
    try:
      normalize.normalize(item, f)
    except:
      util.print_stack()
      continue
    # evaluate the FilteringRules
    skip, rule = filters.evaluate_rules(item, f, feed_uid, exempt)
    filtered_by = None
    if skip:
      skip = -2
      if type(rule.uid) == int:
        filtered_by = rule.uid
      else:
        # XXX clunky convention for feed_rule, but that should disappear
        # XXX eventually
        filtered_by = 0
    title   = item['title']
    link    = item['link']
    guid    = item['id']
    author = item['author']
    created = item['created']
    modified = item['modified']
    if not modified:
      modified = None
    content = item['content']
    # check if the item already exists, using the GUID as key
    c.execute("""select item_uid, item_link,
    item_loaded, item_created, item_modified,
    item_md5hex, item_title, item_content, item_creator
    from fm_items where item_feed_uid=? and item_guid=?""",
              [feed_uid, guid])
    l = c.fetchall()
    # unknown GUID, but title/link duplicate checking may be in effect
    if not l:
      if feed_dupcheck:
        c.execute("""select count(*) from fm_items
        where item_feed_uid=? and (item_title=? or item_link=?)""",
                  [feed_uid, title, link])
        l = bool(c.fetchone()[0])
        if l:
          print >> param.log, 'DUPLICATE TITLE', title
      # XXX Runt items (see normalize.py) are almost always spurious, we just
      # XXX skip them, although we may revisit this decision in the future
      if not l and item.get('RUNT', False):
        print >> param.log, 'RUNT ITEM', item
        l = True
    # GUID already exists, this is a change
    else:
      assert len(l) == 1
      (item_uid, item_link, item_loaded, item_created, item_modified,
       item_md5hex, item_title, item_content, item_creator) = l[0]
      # if this is a feed without timestamps, use our timestamp to determine
      # the oldest item in the feed XML file
      if 'oldest' in f and f['oldest'] == '1970-01-01 00:00:00':
        if 'oldest_ts' not in f:
          f['oldest_ts'] = item_created
        else:
          f['oldest_ts'] = min(f['oldest_ts'], item_created)
      # XXX update item here
      # XXX update tags if required
    # GUID doesn't exist yet, insert it
    if not l:
      # finally, dereference the URL to get rid of annoying tracking servers
      # like feedburner, but only do this once to avoid wasting bandwidth
      link = normalize.dereference(link)
      try:
        c.execute("""insert into fm_items (item_feed_uid, item_guid,
        item_created,   item_modified, item_link, item_md5hex,
        item_title, item_content, item_creator, item_rating, item_rule_uid)
        values
        (?, ?, julianday(?), julianday(?), ?, ?, ?, ?, ?, ?, ?)""",
                  [feed_uid, guid, created, modified, link,
                   md5.new(content).hexdigest(),
                   title, content, author, skip, filtered_by])
        # if we have tags, insert them
        # note: feedparser.py handles 'category' as a special case, so we
        # need to work around that to get to the data
        if item['item_tags']:
          c.execute("""select item_uid
          from fm_items where item_feed_uid=? and item_guid=?""",
                    [feed_uid, guid])
          item_uid = c.fetchone()[0]
          for tag in item['item_tags']:
            c.execute("""insert into fm_tags (tag_name, tag_item_uid)
            values (?, ?)""", [tag, item_uid])
        if skip:
          num_filtered += 1
          print >> param.log, 'SKIP', title, rule
        else:
          num_added += 1
          print >> param.log, ' ' * 4, title
      except:
        util.print_stack(['c', 'f'])
        continue
  # update timestamp of the oldest item still in the feed file
  if 'oldest' in f and f['oldest'] != '9999-99-99 99:99:99':
    if f['oldest'] == '1970-01-01 00:00:00' and 'oldest_ts' in f:
      c.execute("update fm_feeds set feed_oldest=? where feed_uid=?",
                [f['oldest_ts'], feed_uid])
    else:
      c.execute("""update fm_feeds set feed_oldest=julianday(?)
      where feed_uid=?""", [f['oldest'], feed_uid])
  
  return (num_added, num_filtered)

def notification(db, c, feed_uid, title, content):
  """Insert a service notification, e.g. to notify before a feed is disabled
  due to too many errors"""
  hash = md5.new(content).hexdigest()
  guid = 'temboz://%s/%s' % (feed_uid, hash)
  # do nothing if the link is clicked
  link = '/feed_info?feed_uid=%d' % feed_uid
  c.execute("""insert into fm_items (item_feed_uid, item_guid,
  item_created, item_modified, item_link, item_md5hex,
  item_title, item_content, item_creator, item_rating, item_rule_uid)
  values
  (?, ?, julianday('now'), julianday('now'), ?, ?,
  ?, ?, ?, 0, NULL)""",
            [feed_uid, guid, link, hash,
             title, content, 'Temboz notifications'])
  db.commit()

def snr_mv(db, c):
  """SQLite does not have materialized views, so we use a conventional table
instead. The side-effect of this is that new feeds may not be reflected
immediately. The SNR will also lag by up to a day, which should not matter in
practice"""
  c.execute("select sql from sqlite_master where name='update_stat_mv'")
  sql = c.fetchone()
  if sql:
    c.execute('drop trigger update_stat_mv')
  c.execute("select sql from sqlite_master where name='insert_stat_mv'")
  sql = c.fetchone()
  if sql:
    c.execute('drop trigger insert_stat_mv')
  c.execute("select sql from sqlite_master where name='delete_stat_mv'")
  sql = c.fetchone()
  if sql:
    c.execute('drop trigger delete_stat_mv')
  c.execute("select sql from sqlite_master where name='insert_feed_mv'")
  sql = c.fetchone()
  if sql:
    c.execute('drop trigger insert_feed_mv')
  c.execute("select sql from sqlite_master where name='delete_feed_mv'")
  sql = c.fetchone()
  if sql:
    c.execute('drop trigger delete_feed_mv')
  c.execute("select sql from sqlite_master where name='mv_feed_stats'")
  sql = c.fetchone()
  if sql:
    c.execute('drop table mv_feed_stats')
  c.execute("""create table mv_feed_stats (
  snr_feed_uid integer primary key,
  interesting integer default 0,
  unread integer default 0,
  uninteresting integer default 0,
  filtered integer default 0,
  total integer default 0,
  last_modified timestamp,
  snr real default 0.0)""")
  c.execute("""insert into mv_feed_stats
select feed_uid,
sum(case when item_rating=1 then 1 else 0 end),
sum(case when item_rating=0 then 1 else 0 end),
sum(case when item_rating=-1 then 1 else 0 end),
sum(case when item_rating=-2 then 1 else 0 end),
sum(1),
max(item_modified),
snr_decay(item_rating, item_created, ?)
from fm_feeds left outer join (
  select item_rating, item_feed_uid, item_created,
    ifnull(
      julianday(item_modified),
      julianday(item_created)
    ) as item_modified
  from fm_items
) on feed_uid=item_feed_uid
group by feed_uid, feed_title, feed_html, feed_xml""",
          [getattr(param, 'decay', 30)])
  c.execute("select sql from sqlite_master where name='v_feeds_snr'")
  sql = c.fetchone()
  if sql:
    c.execute('drop view v_feeds_snr')
  c.execute("""create view v_feeds_snr as
select feed_uid, feed_title, feed_html, feed_xml,
julianday('now') - last_modified as last_modified,
ifnull(interesting, 0) as interesting,
ifnull(unread, 0) as unread,
ifnull(uninteresting, 0) as uninteresting,
ifnull(filtered, 0) as filtered,
ifnull(total, 0) as total,
ifnull(snr, 0) as snr,
feed_status, feed_private, feed_exempt, feed_errors, feed_desc, feed_filter
from fm_feeds
left outer join mv_feed_stats on feed_uid=snr_feed_uid
group by feed_uid, feed_title, feed_html, feed_xml""")
  c.execute("""create trigger update_stat_mv after update on fm_items
begin
  update mv_feed_stats set
  interesting = interesting
    + case new.item_rating when 1 then 1 else 0 end
    - case old.item_rating when 1 then 1 else 0 end,
  unread = unread
    + case new.item_rating when 0 then 1 else 0 end
    - case old.item_rating when 0 then 1 else 0 end,
  uninteresting = uninteresting
    + case new.item_rating when -1 then 1 else 0 end
    - case old.item_rating when -1 then 1 else 0 end,
  filtered = filtered
    + case new.item_rating when -2 then 1 else 0 end
    - case old.item_rating when -2 then 1 else 0 end,
  last_modified = max(ifnull(last_modified, 0), 
                      ifnull(julianday(new.item_modified),
                             julianday(new.item_created)))
  where snr_feed_uid=new.item_feed_uid;
end""")
  c.execute("""create trigger insert_stat_mv after insert on fm_items
begin
  update mv_feed_stats set
  interesting = interesting
    + case new.item_rating when 1 then 1 else 0 end,
  unread = unread
    + case new.item_rating when 0 then 1 else 0 end,
  uninteresting = uninteresting
    + case new.item_rating when -1 then 1 else 0 end,
  filtered = filtered
    + case new.item_rating when -2 then 1 else 0 end,
  total = total + 1,
  last_modified = max(ifnull(last_modified, 0), 
                      ifnull(julianday(new.item_modified),
                             julianday(new.item_created)))
  where snr_feed_uid=new.item_feed_uid;
end""")
  # XXX there is a possibility last_modified will not be updated if we purge
  # XXX the most recent item. There are no use cases where this could happen
  # XXX since garbage-collection works from the oldest item, and purge-reload
  # XXX will reload the item anyway
  c.execute("""create trigger delete_stat_mv after delete on fm_items
begin
  update mv_feed_stats set
  interesting = interesting
    - case old.item_rating when 1 then 1 else 0 end,
  unread = unread
    - case old.item_rating when 0 then 1 else 0 end,
  uninteresting = uninteresting
    - case old.item_rating when -1 then 1 else 0 end,
  filtered = filtered
    - case old.item_rating when -2 then 1 else 0 end,
  total = total - 1
  where snr_feed_uid=old.item_feed_uid;
end""")
  c.execute("""create trigger insert_feed_mv after insert on fm_feeds
begin
  insert into mv_feed_stats (snr_feed_uid) values (new.feed_uid);
end""")
  # XXX there is a possibility last_modified will not be updated if we purge
  # XXX the most recent item. There are no use cases where this could happen
  # XXX since garbage-collection works from the oldest item, and purge-reload
  # XXX will reload the item anyway
  c.execute("""create trigger delete_feed_mv after delete on fm_feeds
begin
  delete from mv_feed_stats
  where snr_feed_uid=old.feed_uid;
end""")
  db.commit()  

def cleanup(db=None, c=None):
  """garbage collection - see param.py
  this is done only once a day between 3 and 4 AM as this is quite intensive
  and could interfere with user activity
  It can also be invoked by running temboz --clean
  """
  if not db:
    from singleton import db
    c = db.cursor()
  from singleton import sqlite_cli
  if getattr(param, 'garbage_contents', False):
    c.execute("""update fm_items set item_content=''
    where item_rating < 0 and item_created < julianday('now')-?""",
              [param.garbage_contents])
    db.commit()
  if getattr(param, 'garbage_items', False):
    c.execute("""delete from fm_items where item_uid in (
      select item_uid from fm_items, fm_feeds
      where item_created < min(julianday('now')-?, feed_oldest-7)
      and item_rating<0 and feed_uid=item_feed_uid)""", [param.garbage_items])
    db.commit()
  snr_mv(db, c)
  c.execute("""delete from fm_tags
  where not exists(
    select item_uid from fm_items where item_uid=tag_item_uid
  )""")
  db.commit()
  c.execute('vacuum')
  # we still hold the PseudoCursor lock, this is a good opportunity to backup
  try:
    os.mkdir('backups')
  except OSError:
    pass
  os.system((sqlite_cli + ' rss.db .dump | %s > backups/daily_' \
             + time.strftime('%Y-%m-%d') + '%s') % param.backup_compressor)
  # rotate the log
  os.rename('temboz.log', 'backups/log_' + time.strftime('%Y-%m-%d'))
  param.log.close()
  param.log = open(param.log_filename, 'a', 0)
  os.dup2(param.log.fileno(), 1)
  os.dup2(param.log.fileno(), 2)
  # delete old backups
  backup_re = re.compile(
    'daily_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\\.')
  log_re = re.compile(
    'log_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
  for fn in os.listdir('backups'):
    if backup_re.match(fn) or log_re.match(fn):
      elapsed = time.time() - os.stat('backups/' + fn).st_ctime
      if elapsed > 86400 * param.daily_backups:
        try:
          os.remove('backups/' + fn)
        except OSError:
          pass
  
def update(where_clause=''):
  from singleton import db
  c = db.cursor()
  # refresh filtering rules
  filters.load_rules(db, c)
  # at 3AM by default, perform house-cleaning
  if time.localtime()[3] == param.backup_hour:
    cleanup(db, c)
  # create worker threads and the queues used to communicate with them
  work_q = Queue.Queue()
  process_q = Queue.Queue()
  workers = []
  for i in range(param.feed_concurrency):
    workers.append(FeedWorker(i + 1, work_q, process_q))
    workers[-1].start()
  # assign work
  c.execute("""select feed_uid, feed_xml, feed_etag, feed_dupcheck,
  strftime('%s', feed_modified) from fm_feeds where feed_status=0 """
            + where_clause)
  for feed_uid, feed_xml, feed_etag, feed_dupcheck, feed_modified in c:
    if feed_modified:
      feed_modified = float(feed_modified)
      feed_modified = time.localtime(feed_modified)
    else:
      feed_modified = None
    work_q.put((feed_uid, feed_xml, feed_etag, feed_modified, feed_dupcheck))
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
      try:
        update_feed(db, c, *feed_info)
      except:
        util.print_stack()
      db.commit()
    # give reader threads an opportunity to get their work done
    time.sleep(1)
  c.close()

class PeriodicUpdater(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.setDaemon(True)
  def run(self):
    while True:
      # XXX should wrap this in a try/except clause
      time.sleep(param.refresh_interval)
      print >> param.log, time.ctime(), '- refreshing feeds'
      try:
        update()
      except:
        util.print_stack()

def view_sql(c, where, sort, params, overload_threshold):
  c.execute("""create temp table articles as select
    item_uid, item_creator, item_title, item_link, item_content,
    datetime(item_loaded), date(item_created) as item_created,
    julianday('now') - julianday(item_created) as delta_created, item_rating,
    item_rule_uid, item_feed_uid, feed_title, feed_html, feed_xml
  from fm_items, v_feeds_snr
  where item_feed_uid=feed_uid and """ + where + """
  order by """ + sort + """ limit ?""",
  params + [overload_threshold])
  c.execute("""create index articles_i on articles(item_uid)""")
  c.execute("""select tag_item_uid, tag_name, tag_by
  from  fm_tags, articles where tag_item_uid=item_uid""")
  tag_dict = dict()
  for item_uid, tag_name, tag_by in c:
    tag_dict.setdefault(item_uid, []).append(tag_name)
  c.execute("""select * from articles
  order by """ + sort + """, item_uid DESC""")
  return tag_dict
