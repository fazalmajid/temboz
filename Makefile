WW_FILE:sh	=echo ../../src/lang/python/Webware-*.tar.gz
WW_VER=		$(WW_FILE:../../src/lang/python/Webware-%.tar.gz=%)

PAGES=	error unread


all: cheetah

cheetah:$(PAGES:%=pages/%.py)
pages/%.py: pages/%.tmpl
	cheetah compile $<

init:
	-rm -f rss.db
	sqlite rss.db < ddl.sql > /dev/null
	#temboz --import subs.opml
	temboz --import fof.opml
	#temboz --import broken.opml
	#temboz --import me.opml
	temboz --refresh

sync:
	-mv feedparser.py feedparser.old
	wget http://diveintomark.org/projects/feed_parser/feedparser.py

webware: Webware-$(WW_VER)/_installed
Webware-$(WW_VER)/_installed: $(WW_FILE)
	gzip -cd $(WW_FILE)|tar xf -
	expect webware.exp

clean:
	-rm -f core *.pyc *~ *.old

realclean: clean
	-rm -rf Webware*  rss.db
