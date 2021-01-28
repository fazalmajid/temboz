from __future__ import print_function
import sys, time, sqlite3, string, json
from . import param

def db():
  conn = sqlite3.connect('rss.db', 60.0)
  conn.row_factory = sqlite3.Row
  return conn

def rebuild_v_feed_stats(c):
  sql = c.execute("select sql from sqlite_master where name='v_feeds_snr'")
  if sql:
    c.executescript("""
    drop view if exists v_feeds_snr;
    create view v_feeds_snr as
    select feed_uid, feed_title, feed_html, feed_xml, feed_pubxml,
      julianday('now') - last_modified as last_modified,
      ifnull(interesting, 0) as interesting,
      ifnull(unread, 0) as unread,
      ifnull(uninteresting, 0) as uninteresting,
      ifnull(filtered, 0) as filtered,
      ifnull(total, 0) as total,
      ifnull(snr, 0) as snr,
      feed_status, feed_private, feed_exempt, feed_dupcheck, feed_errors,
      feed_desc, feed_filter
    from fm_feeds
    left outer join mv_feed_stats on feed_uid=snr_feed_uid
    group by feed_uid, feed_title, feed_html, feed_xml;""")

def snr_mv(db, c):
  """SQLite does not have materialized views, so we use a conventional table
instead. The side-effect of this is that new feeds may not be reflected
immediately. The SNR will also lag by up to a day, which should not matter in
practice"""
  sql = c.execute("select sql from sqlite_master where name='update_stat_mv'")
  if sql:
    c.execute('drop trigger if exists update_stat_mv')
  sql = c.execute("select sql from sqlite_master where name='insert_stat_mv'")
  if sql:
    c.execute('drop trigger if exists insert_stat_mv')
  sql = c.execute("select sql from sqlite_master where name='delete_stat_mv'")
  if sql:
    c.execute('drop trigger if exists delete_stat_mv')
  sql = c.execute("select sql from sqlite_master where name='insert_feed_mv'")
  if sql:
    c.execute('drop trigger if exists insert_feed_mv')
  sql = c.execute("select sql from sqlite_master where name='delete_feed_mv'")
  if sql:
    c.execute('drop trigger if exists delete_feed_mv')
  sql = c.execute("select sql from sqlite_master where name='mv_feed_stats'")
  if sql:
    c.execute('drop table if exists mv_feed_stats')
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
  with feeds as (
  select feed_uid,
    sum(case when item_rating=1 then 1 else 0 end)  interesting,
    sum(case when item_rating=0 then 1 else 0 end)  unread,
    sum(case when item_rating=-1 then 1 else 0 end) uninteresting,
    sum(case when item_rating=-2 then 1 else 0 end) filtered,
    sum(1)                                          total,
    max(item_modified)                              latest,
    sum(case when item_rating > 0 then 1.0 else 0 end
        / (1 << min(62, (julianday('now') - item_created)/%(decay)d)))
                                                    snr_sig,
    sum(1.0
        / (1 << min(62, (julianday('now') - item_created)/%(decay)d)))
                                                    snr_norm
  from fm_feeds left outer join (
    select item_rating, item_feed_uid, item_created,
      ifnull(
        julianday(item_modified),
        julianday(item_created)
      ) as item_modified
    from fm_items
  ) on feed_uid=item_feed_uid
  group by feed_uid, feed_title, feed_html, feed_xml
  )
  select feed_uid, interesting, unread, uninteresting, filtered, total,
    latest,
    case when snr_norm=0 then 0
         when snr_norm is null or snr_sig is null then 0
         else snr_sig / snr_norm
    end as snr
  from feeds""" % {
    'decay': getattr(param, 'decay', 30)
  })
  rebuild_v_feed_stats(c)
  c.executescript("""
  create trigger update_stat_mv after update on fm_items
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
  end;
  create trigger insert_stat_mv after insert on fm_items
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
  end;""")
  # XXX there is a possibility last_modified will not be updated if we purge
  # XXX the most recent item. There are no use cases where this could happen
  # XXX since garbage-collection works from the oldest item, and purge-reload
  # XXX will reload the item anyway
  c.executescript("""
  create trigger delete_stat_mv after delete on fm_items
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
  end;
  create trigger insert_feed_mv after insert on fm_feeds
  begin
    insert into mv_feed_stats (snr_feed_uid) values (new.feed_uid);
  end;
  create trigger delete_feed_mv after delete on fm_feeds
  begin
    delete from mv_feed_stats
    where snr_feed_uid=old.feed_uid;
  end;""")
  db.commit()

def mv_on_demand(db):
  """creating the materialized view is not more expensive than running the
  slow full table scan way, so we do so on demand (rather than at startup)"""
  c = db.cursor()
  sql = c.execute("select sql from sqlite_master where name='mv_feed_stats'")
  status = c.fetchone()
  if not status:
    print('WARNING: rebuilding mv_feed_stats...', end=' ', file=param.log)
    snr_mv(db, c)
    db.commit()
    print('done', file=param.log)
  c.close()

def elapsed(t, what):
  t2 = time.time()
  print(what, (t2-t)* 1000, 'ms', file=param.log)
  return t2

use_json = None
def view_sql(c, where, sort, params, overload_threshold):
  global use_json
  if use_json is None:
    try:
      c.execute("""select json_group_array(feed_uid) from fm_feeds""")
      use_json = True
    except:
      use_json = False
  if use_json:
    return view_sql_json(c, where, sort, params, overload_threshold)
  else:
    view_sql_no_json(c, where, sort, params, overload_threshold)
    
def view_sql_no_json(c, where, sort, params, overload_threshold):
  t = time.time()
  mv_on_demand(c)
  #t = elapsed(t, 'mv_on_demand')
  c.execute('drop table if exists articles')
  #t = elapsed(t, 'drop table if exists article')
  c.execute("""create table articles as select
    item_uid, item_creator, item_title, item_link, item_content,
    datetime(item_loaded), date(item_created) as item_created,
    datetime(item_rated) as item_rated,
    julianday('now') - julianday(item_created) as delta_created, item_rating,
    item_rule_uid, item_feed_uid, feed_title, feed_html, feed_xml,
    ifnull(snr, 0) as snr, updated, feed_exempt
  from fm_items
  join fm_feeds on item_feed_uid=feed_uid
  left outer join mv_feed_stats on feed_uid=snr_feed_uid
  where item_feed_uid=feed_uid and """ + where + """
  order by """ + sort + """, item_uid DESC limit ?""",
            params + [overload_threshold])
  #t = elapsed(t, 'create table articles')
  c.execute("""create index articles_i on articles(item_uid)""")
  #t = elapsed(t, 'create index articles_i')
  tag_dict = dict()
  for item_uid, tag_name, tag_by in c.execute(
      """select tag_item_uid, tag_name, tag_by
      from fm_tags, articles where tag_item_uid=item_uid"""):
    tag_dict.setdefault(item_uid, []).append(tag_name)
  output = c.execute("""select * from articles
  order by """ + sort + """, item_uid DESC""")
  #t = elapsed(t, 'output')
  return tag_dict, output

def view_sql_json(c, where, sort, params, overload_threshold):
  mv_on_demand(c)
  rows = c.execute("""select
    item_uid, item_creator, item_title, item_link, item_content,
    datetime(item_loaded), date(item_created) as item_created,
    datetime(item_rated) as item_rated,
    julianday('now') - julianday(item_created) as delta_created, item_rating,
    item_rule_uid, item_feed_uid, feed_title, feed_html, feed_xml,
    ifnull(snr, 0) as snr, updated, feed_exempt,
    json_group_array(tag_name)
  from fm_items
  join fm_feeds on item_feed_uid=feed_uid
  left outer join mv_feed_stats on feed_uid=snr_feed_uid
  left outer join fm_tags on tag_item_uid=item_uid
  where item_feed_uid=feed_uid and """ + where + """
  group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
  order by """ + sort + """, item_uid DESC limit ?""",
            params + [overload_threshold])
  tag_dict = dict()
  output = []
  for cols in rows:
    cols = list(cols)
    output.append(cols[:-1])
    tags = json.loads(cols[-1])
    tag_dict[cols[0]] = tags
  return tag_dict, output

def feed_info_sql(c, feed_uid):
  mv_on_demand(c)
  return c.execute("""select feed_title, feed_desc, feed_filter,
  feed_html, feed_xml, feed_pubxml,
  last_modified, interesting, unread, uninteresting, filtered, total,
  feed_status, feed_private, feed_exempt, feed_dupcheck, feed_errors
  from v_feeds_snr
  where feed_uid=?
  group by feed_uid, feed_title, feed_html, feed_xml
  """, [feed_uid])

def top_rules(c, feed_uid):
  return c.execute("""select item_rule_uid, rule_type, rule_text, count(*)
  from fm_items
  join fm_rules on rule_uid=item_rule_uid
  where item_feed_uid=? and item_rating=-2
  group by 1, 2, 3 order by 4 DESC, 3
  limit 25""", [feed_uid])

def rules(c, feed_uid=None):
  if feed_uid:
    rows = c.execute("""
    select rule_uid, rule_type, date(rule_expires), rule_text
    from fm_rules
    where rule_feed_uid=?
    order by lower(rule_text)""", [feed_uid])
  else:
    rows = c.execute("""
    select rule_uid, rule_type, date(rule_expires), rule_text
    from fm_rules
    where rule_feed_uid is NULL
    order by lower(rule_text)""")
  tabs = {}
  for uid, rtype, expires, text in rows.fetchall():
    row = uid, rtype, expires, text
    initial = text[0].upper()
    if rtype == 'python':
      tab = 'Python'
    elif initial not in string.ascii_uppercase:
      tab = '0'
    else:
      tab = initial
    tabs.setdefault(tab, list()).append(row)
  return tabs

def stats(c):
  return c.execute("""select date(item_loaded) as date, count(*) as articles,
    sum(case when item_rating=1 then 1 else 0 end) as interesting,
    sum(case when item_rating=0 then 1 else 0 end) as unread,
    sum(case when item_rating=-1 then 1 else 0 end) as filtered
  from fm_items
  where item_loaded > julianday('now') - 30
  group by 1 order by 1""")

def share(c):
  return c.execute("""select item_guid, item_creator, item_title, item_link,
    item_content, feed_title,
    strftime('%Y-%m-%dT%H:%M:%SZ', item_created)
  from fm_items, fm_feeds where item_feed_uid=feed_uid
  and item_rating=1 and feed_private = 0
  order by item_rated DESC, item_uid DESC
  limit 50""")

def feeds(db, sort_key, order):
  assert sort_key == '(unread > 0) DESC, snr' or sort_key in {
    'feed_title', 'lower(feed_title)', 'last_modified', 'unread', 'filtered',
    'interesting', 'snr', 'total'
  }, repr(sort_key)
  assert order in ('ASC', 'DESC')
  c = db.cursor()
  c.execute("""select feed_uid, feed_title, feed_html, feed_xml,
  last_modified, interesting, unread, uninteresting, filtered, total,
  snr, feed_status, feed_private, feed_exempt, feed_errors,
  feed_filter notnull
  from v_feeds_snr
  order by feed_status ASC, """ \
                 + sort_key + ' ' + order + """, lower(feed_title)""")
  return c.fetchall()

def opml(db):
  c = db.cursor()
  c.execute("""select feed_uid, feed_title, feed_desc,
  feed_html, coalesce(feed_pubxml, feed_xml) as feed_xml, snr
  from v_feeds_snr
  where feed_status=0 and feed_private=0
  order by snr desc, lower(feed_title)""")
  return c.fetchall()

def item(db, uid):
  c = db.cursor()
  c.execute("""select item_title, item_content, item_link
  from fm_items where item_uid=?""", [uid])
  return c.fetchone()

def setting(db, *args, **kwargs):
  c = db.cursor()
  for name, value in list(zip(args[::2], args[1::2])) + list(kwargs.items()):
    param.settings[name] = str(value)
    try:
      c.execute("insert into fm_settings (name, value) values (?, ?)",
                [name, str(value)])
    except sqlite3.IntegrityError as e:
      c.execute("update fm_settings set value=? where name=?",
                [value, name])
  db.commit()
  c.close()

def get_setting(db, name, default):
  c = db.cursor()
  c.execute('select value from fm_settings where name=?', [name])
  l = c.fetchone()
  c.close()
  if not l:
    return default
  else:
    return l[0]

def load_settings(c):
  c.execute("select name, value from fm_settings")
  setattr(param, 'settings', dict(c.fetchall()))

fts_enabled = False
def fts(d, c):
  global fts_enabled
  sql = c.execute("select sql from sqlite_master where name='search'")
  status = c.fetchone()
  if status:
    fts_enabled = True
  else:
    try:
      c.execute("""create virtual table if not exists search
      using fts5(content="fm_items", item_title, item_content,
                 content_rowid=item_uid)""")
      # Triggers to keep the FTS index up to date.
      c.execute("""create trigger fts_ai after insert on fm_items
      begin
        insert into search(rowid, item_title, item_content)
        values (NEW.item_uid, NEW.item_title, NEW.item_content);
      end;""")
      c.execute("""create trigger fts_ad after delete on fm_items
      begin
        insert into search(search, rowid, item_title, item_content)
        values ('delete', OLD.item_uid, OLD.item_title, OLD.item_content);
      end;""")
      c.execute("""create trigger fts_au after update on fm_items
      begin
        insert into search(search, rowid, item_title, item_content)
        values ('delete', OLD.item_uid, OLD.item_title, OLD.item_content);
        insert into search(rowid, item_title, item_content)
        values (NEW.item_uid, NEW.item_title, NEW.item_content);
      end;""")
      c.execute("""insert into search(search) values ('rebuild')""")
      d.commit()
      fts_enabled = True
    except:
      d.rollback()
      fts_enabled = False

def sync_col(d, c):
  c.execute("""pragma journal_mode=WAL""")
  sql = c.execute("""select * from sqlite_master
  where tbl_name='fm_items' and sql like '%updated%'""")
  status = c.fetchone()
  if not status:
    try:
      # create an updated column on fm_items with corresponding triggers
      # to maintain it. This will be used to sync offline mode
      c.execute("""alter table fm_items add column updated timestamp""")
      c.execute("""update fm_items set updated = julianday('now')""")
      c.execute("""create trigger insert_items_ts after insert on fm_items
      for each row begin update fm_items
      set updated=julianday('now')
      where item_uid=NEW.item_uid; end""")
      c.execute("""create trigger update_items_ts after update on fm_items
      for each row begin update fm_items
      set updated=julianday('now')
      where item_uid=NEW.item_uid; end""")
      c.execute("""create index item_updated_i on fm_items(updated)""")
      d.commit()
    except:
      d.rollback()

def sessions(d, c):
  sql = c.execute("""select * from sqlite_master
  where tbl_name='fm_sessions'""")
  status = c.fetchone()
  if not status:
    try:
      # create an updated column on fm_items with corresponding triggers
      # to maintain it. This will be used to sync offline mode
      c.execute("""create table fm_sessions (
      uuid text primary key,
      user_agent text,
      created timestamp default (julianday('now')),
      expires timestamp default (julianday('now') + 14)
      )""")
      d.commit()
    except:
      d.rollback()

def save_session(uuid, user_agent):
  with db() as d:
    c = d.cursor()
    try:
      c.execute("""delete from fm_sessions where expires < julianday('now')""")
      c.execute("""insert into fm_sessions (uuid, user_agent) values (?, ?)""",
                [uuid, user_agent])
      d.commit()
      auth_cache[uuid, user_agent] = time.time() + 14 * 86400
    except sqlite3.IntegrityError:
      pass

auth_cache = dict()
def check_session(uuid, user_agent):
  if (uuid, user_agent) in auth_cache \
     and time.time() < auth_cache[uuid, user_agent]:
    return True
  with db() as d:
    c = d.cursor()
    c.execute("""select count(*), MAX((expires - 2440587.5)*86400)
    from fm_sessions
    where uuid=? and user_agent=? and expires > julianday('now')
      and created < julianday('now')""", [uuid, user_agent])
    l = c.fetchone()
    good = l and l[0] == 1
    if good:
      auth_cache[uuid, user_agent] = l[1]
    return good

with db() as d:
  c = d.cursor()
  load_settings(c)
  mv_on_demand(d)
  rebuild_v_feed_stats(d)
  d.commit()
  fts(d, c)
  sync_col(d, c)
  sessions(d, c)
  c.close()
