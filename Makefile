VERSION= 0.5
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

dist: distclean changelog
	-rm -rf temboz-$(VERSION)
	mkdir temboz-$(VERSION)
	cp README INSTALL NEWS LICENSE UPGRADE ChangeLog temboz *.py temboz-$(VERSION)
	cp ddl.sql me.opml temboz-$(VERSION)
	cp -r pages images etc temboz-$(VERSION)
	-rm -f temboz-$(VERSION)/etc/.cvsignore
	-rm -rf temboz-$(VERSION)/pages/CVS temboz-$(VERSION)/images/CVS
	-rm -rf temboz-$(VERSION)/etc/CVS
	# expurgate password
	sed -e 's/auth_dict.*/auth_dict={"login": "password"}/g' param.py > temboz-$(VERSION)/param.py
	gtar zcvf temboz-$(VERSION).tar.gz temboz-$(VERSION)
	-rm -rf temboz-$(VERSION)
	-mv temboz-$(VERSION).tar.gz ../mylos/data/stories/2004/03/29
	-$${EDITOR} ../mylos/data/stories/2004/03/29/temboz.html

distclean:
	-rm -f core *.pyc *~ pages/*~ *.old pages/*.py ChangeLog*
	-find . -name .\#* -exec rm {} \;
	-find . -name .\#~ -exec rm {} \;
	-rm -f pages/*~

clean: distclean
	-rm -rf temboz-$(VERSION) temboz-$(VERSION).tar.gz

realclean: clean
	-rm -rf rss.db
