import sqlite3
import param

def db():
  conn = sqlite3.connect('rss.db', 120.0)
  conn.row_factory = sqlite3.Row
  return conn

def rebuild_v_feed_stats(c):
  sql = c.execute("select sql from sqlite_master where name='v_feeds_snr'")
  if sql:
    c.executescript("""
    drop view v_feeds_snr;
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

def snr_mv(c):
  """SQLite does not have materialized views, so we use a conventional table
instead. The side-effect of this is that new feeds may not be reflected
immediately. The SNR will also lag by up to a day, which should not matter in
practice"""
  sql = c.execute("select sql from sqlite_master where name='update_stat_mv'")
  if sql:
    c.execute('drop trigger update_stat_mv')
  sql = c.execute("select sql from sqlite_master where name='insert_stat_mv'")
  if sql:
    c.execute('drop trigger insert_stat_mv')
  sql = c.execute("select sql from sqlite_master where name='delete_stat_mv'")
  if sql:
    c.execute('drop trigger delete_stat_mv')
  sql = c.execute("select sql from sqlite_master where name='insert_feed_mv'")
  if sql:
    c.execute('drop trigger insert_feed_mv')
  sql = c.execute("select sql from sqlite_master where name='delete_feed_mv'")
  if sql:
    c.execute('drop trigger delete_feed_mv')
  sql = c.execute("select sql from sqlite_master where name='mv_feed_stats'")
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
  c.commit()  

def mv_on_demand(c):
  """creating the materialized view is not more expensive than running the
  slow full table scan way, so we do so on demand (rather than at startup)"""
  sql = c.execute("select sql from sqlite_master where name='mv_feed_stats'")
  if not sql:
    print >> param.log, 'WARNING: rebuilding mv_feed_stats...',
    snr_mv(c)
    print >> param.log, 'done'

def view_sql(c, where, sort, params, overload_threshold):
  mv_on_demand(c)
  c.execute('drop table if exists articles')
  c.execute("""create table articles as select
    item_uid, item_creator, item_title, item_link, item_content,
    datetime(item_loaded), date(item_created) as item_created,
    datetime(item_rated) as item_rated,
    julianday('now') - julianday(item_created) as delta_created, item_rating,
    item_rule_uid, item_feed_uid, feed_title, feed_html, feed_xml, snr
  from fm_items, v_feeds_snr
  where item_feed_uid=feed_uid and """ + where + """
  order by """ + sort + """, item_uid DESC limit ?""",
            params + [overload_threshold])
  c.execute("""create index articles_i on articles(item_uid)""")
  tag_dict = dict()
  for item_uid, tag_name, tag_by in c.execute(
      """select tag_item_uid, tag_name, tag_by
      from fm_tags, articles where tag_item_uid=item_uid"""):
    tag_dict.setdefault(item_uid, []).append(tag_name)
  return tag_dict, c.execute("""select * from articles
  order by """ + sort + """, item_uid DESC""")

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

c = db()
mv_on_demand(c)
rebuild_v_feed_stats(c)
c.commit()
c.close()

