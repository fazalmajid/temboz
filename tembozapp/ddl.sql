create table fm_feeds (
	feed_uid	integer primary key,
	feed_xml	varchar(255) unique not null,
	feed_pubxml	varchar(255),
	feed_etag	varchar(255),
	feed_modified	varchar(255),
	feed_html	varchar(255) not null,
	feed_title	varchar(255),
	feed_desc	text,
	feed_errors	int default 0,
	feed_lang	varchar(2) default 'en',
	feed_private	int default 0,
	feed_dupcheck	int default 0,
	feed_oldest	timestamp,
	-- 0=active, 1=suspended
	feed_status	int default 0,
	-- 0=hourly, 1=daily, 2=weekly, 3=monthly
	feed_frequency	int default 0,
	feed_auth	varchar(255),
	feed_filter	text,
	feed_exempt	int default 0
);

create table fm_items (
	item_uid	integer primary key,
	item_guid	varchar(255),
	item_feed_uid	integer
	references fm_feeds (feed_uid) on delete cascade,
	item_loaded	timestamp,
	item_created	timestamp,
	item_modified	timestamp,
	item_rated	timestamp,
	item_link	varchar(255),
	item_md5hex	char(32) not null,
	item_title	text,
	item_content	text,
	item_creator	varchar(255),
	-- 1=interesting, 0=unread, -1=uninteresting, -2=filtered
	item_rating	integer default 0
	check (item_rating between -2 and +1),
	item_item_uid	integer, -- to cluster related items together
	item_rule_uid	integer
	references fm_rules (rule_uid) on delete cascade
);

create trigger update_timestamp after insert on fm_items
begin
	update fm_items set item_loaded = julianday("now")
	where item_uid=new.item_uid;
end;

create index item_feed_link_i on fm_items(item_feed_uid, item_link);
create unique index item_feed_guid_i on fm_items(item_feed_uid, item_guid);
create index item_rating_i on fm_items(item_rating, item_feed_uid);
create index item_title_i on fm_items(item_feed_uid, item_title);

create table fm_rules (
	rule_uid	integer primary key,
	rule_type	varchar(16) not null default 'python',
	rule_feed_uid	integer
	references fm_feeds (feed_uid) on delete cascade,
	rule_expires	timestamp,
	rule_text	text
);

create table fm_tags (
	tag_name	varchar(64) not null,
	tag_item_uid	integer not null
	references fm_items (item_uid) on delete cascade,
	-- 0=by the feed, 1=by the user, 2=by an algorithm
	tag_by		integer default 0
	check (tag_by between 0 and 2),
	primary key(tag_item_uid, tag_name, tag_by)
);
create index fm_tags_name_i on fm_tags (tag_name);

create table fm_settings (
	name		varchar(255) primary key,
	value		text not null
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
