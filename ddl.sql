create table fm_feeds (
	feed_uid	integer primary key,
	feed_xml	varchar(255) unique not null,
	feed_etag	varchar(255),
	feed_modified	varchar(255),
	feed_html	varchar(255) not null,
	feed_title	varchar(255),
	feed_desc	text,
	feed_errors	int default 0,
	-- 0=active, 1=suspended
	feed_status	int default 0
);

create table fm_items (
	item_uid	integer primary key,
	item_feed_uid	int,
	-- references fm_feeds (feed_uid) on delete cascade,
	item_loaded	timestamp,
	item_created	timestamp,
	item_modified	timestamp,
	item_viewed	timestamp,
	item_link	varchar(255),
	item_md5hex	char(32) not null,
	item_title	text,
	item_content	text,
	item_creator	varchar(255),
	item_rating	default 0
);

create trigger update_timestamp after insert on fm_items
begin
	update fm_items set item_loaded = julianday("now")
	where item_uid=new.item_uid;
end;

create unique index item_feed_link_i on fm_items(item_feed_uid, item_link);

create table fm_rules (
	rule_uid	integer primary key,
	rule_expires	timestamp,
	rule_text	text
);

create view top20 as
  select
    feed_title,
    round(100*interesting/(interesting+uninteresting)) as interest_ratio
  from (
    select
      feed_title,
      sum(case when item_rating=1 then 1 else 0 end) as interesting,
      sum(case when item_rating=-1 then 1 else 0 end) as uninteresting
    from fm_feeds, fm_items
    where item_feed_uid=feed_uid
    group by feed_title
    order by feed_title
  )
order by interest_ratio DESC
limit 20;

create view daily_stats as
  select
    date(item_created) as day,
    sum(case when item_rating>0 then 1 else 0 end) as interesting,
    sum(case when item_rating=-2 then 1 else 0 end) as filtered,
    sum(case when item_rating=-1 then 1 else 0 end) as uninteresting
  from fm_feeds, fm_items
  where item_feed_uid=feed_uid
  group by day
  order by day;
