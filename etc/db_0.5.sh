#!/bin/sh
mkdir backups || true
gzip -c9 rss.db > backups/rss.db.pre-0.5,gz
echo "backup done"
sqlite rss.db <<EOF

create table fm_items2 (
	item_uid	integer primary key,
	item_guid	varchar(255),
	item_feed_uid	int,
	item_loaded	timestamp,
	item_created	timestamp,
	item_modified	timestamp,
	item_viewed	timestamp,
	item_link	varchar(255),
	item_md5hex	char(32) not null,
	item_title	text,
	item_content	text,
	item_creator	varchar(255),
	item_rating	default 0,
	item_item_uid	int
);

insert into fm_items2 select item_uid, item_link, item_feed_uid, item_loaded, item_created, item_modified, item_viewed, item_link, item_md5hex, item_title, item_content, item_creator, item_rating, null from fm_items;

drop table fm_items;
create table fm_items (
	item_uid	integer primary key,
	item_guid	varchar(255),
	item_feed_uid	int,
	item_loaded	timestamp,
	item_created	timestamp,
	item_modified	timestamp,
	item_viewed	timestamp,
	item_link	varchar(255),
	item_md5hex	char(32) not null,
	item_title	text,
	item_content	text,
	item_creator	varchar(255),
	item_rating	default 0,
	item_item_uid	int
);

insert into fm_items select * from fm_items2;
create trigger update_timestamp after insert on fm_items
begin
	update fm_items
	set
	        item_loaded = julianday("now"),
		item_item_uid = coalesce(item_item_uid, item_uid)
	where item_uid=new.item_uid;
end;

create index item_feed_link_i on fm_items(item_feed_uid, item_link);
create unique index item_feed_guid_i on fm_items(item_feed_uid, item_guid);
create index item_rating_i on fm_items(item_rating, item_feed_uid);
create index item_title_i on fm_items(item_feed_uid, item_title);

drop table fm_items2;

create table fm_feeds2 (
	feed_uid	integer primary key,
	feed_xml	varchar(255) unique not null,
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
	feed_status	int default 0
);

insert into fm_feeds2 select feed_uid, feed_xml, feed_etag, feed_modified,
feed_html, feed_title, feed_desc, feed_errors, 'en', 0, 0, null, feed_status
from fm_feeds;

drop table fm_feeds;
create table fm_feeds (
	feed_uid	integer primary key,
	feed_xml	varchar(255) unique not null,
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
	feed_status	int default 0
);
insert into fm_feeds select * from fm_feeds2;
drop table fm_feeds2;

vacuum;
EOF
