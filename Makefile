VERSION= 0.3.1
PAGES= view error opml feeds temboz.css rules catch_up

all: changelog

cheetah: $(PAGES:%=pages/%.py)
pages/%.py: pages/%.tmpl
	cheetah compile $<

init:
	@if [ `hostname` != "alamut" ]; then true; else echo "Will not run make init on alamut"; false; fi
	-rm -f rss.db
	sqlite rss.db < ddl.sql > /dev/null
	temboz --import me.opml
	temboz --refresh

sync:
	-mv feedparser.py feedparser.old
	wget http://diveintomark.org/projects/feed_parser/feedparser.py

changelog:
	cvs2cl.pl --tags -g -q

dist: changelog
	-rm -rf temboz-$(VERSION)
	mkdir temboz-$(VERSION)
	cp README INSTALL ChangeLog temboz *.py rss.db.dump temboz-$(VERSION)
	cp ddl.sql me.opml temboz-$(VERSION)
	-rm -f pages/*~
	cp -r pages images temboz-$(VERSION)
	-rm -rf temboz-$(VERSION)/pages/CVS temboz-$(VERSION)/images/CVS
	# expurgate password
	sed -e 's/auth_dict.*/auth_dict={"login": "password"}/g' param.py > temboz-$(VERSION)/param.py
	gtar zcvf temboz-$(VERSION).tar.gz temboz-$(VERSION)
	-rm -rf temboz-$(VERSION)

clean:
	-rm -f core *.pyc *~ pages/*~ *.old pages/*.py ChangeLog*
	-rm -rf temboz-$(VERSION) temboz-$(VERSION).tar.gz

realclean: clean
	-rm -rf rss.db
