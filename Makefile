VERSION= 	0.8
TAR_VERSION=	$(VERSION)
PAGES= 		view error opml feeds temboz_css rules catch_up
DATE:sh=	date +'%Y-%m-%d'

all: changelog

cheetah: $(PAGES:%=pages/%.py)
pages/%.py: pages/%.tmpl
	cheetah compile $<
	python -m py_compile pages/*.py

init:
	@if [ `hostname` != "alamut" ]; then true; else echo "Will not run make init on alamut"; false; fi
	-rm -f rss.db
	sqlite3 rss.db < ddl.sql > /dev/null
	temboz --import me.opml
	temboz --refresh

sync:
	-mv feedparser.py feedparser.old
	wget http://diveintomark.org/projects/feed_parser/feedparser.py

changelog:
	cvs2cl.pl --tags -g -q

cvsdist :=  TAR_VERSION = CVS
cvsdist :=  VERSION = CVS-$(DATE)
cvsdist:: cvsupdate
cvsupdate:
	cvs -q update -A -d -P
cvsdist disttar:: distclean changelog
	-rm -rf temboz-$(VERSION)
	mkdir temboz-$(VERSION)
	-rm -f .*~ *~
	cp README INSTALL NEWS LICENSE UPGRADE ChangeLog temboz *.py temboz-$(VERSION)
	cp ddl.sql me.opml .ht* temboz-$(VERSION)
	cp -r pages images etc temboz-$(VERSION)
	(cd temboz-$(VERSION); mv param.py param.py.sample; mv transform.py transform.py.sample)
	-rm -f temboz-$(VERSION)/etc/.cvsignore
	-rm -rf temboz-$(VERSION)/pages/CVS temboz-$(VERSION)/images/CVS
	-rm -rf temboz-$(VERSION)/etc/CVS
	# expurgate password
	sed -e 's/auth_dict.=.*/auth_dict = {"login": "password"}/g' param.py > temboz-$(VERSION)/param.py
	gtar zcvf temboz-$(TAR_VERSION).tar.gz temboz-$(VERSION)
	-rm -rf temboz-$(VERSION)
	-mv temboz-$(TAR_VERSION).tar.gz ../mylos/data/stories/2004/03/29

dist: disttar
	-$${EDITOR} ../mylos/data/stories/2004/03/29/temboz.html

distclean:
	-rm -f core *.pyc *~ pages/*~ *.old pages/*.py pages/*.pyc ChangeLog*
	-find . -name .\#* -exec rm {} \;
	-find . -name .\#~ -exec rm {} \;
	-rm -f pages/*~

clean: distclean
	-rm -rf temboz-$(VERSION) temboz-$(VERSION).tar.gz
	-rm -f pages/*.py pages/*.pyc pages/*.pyo pages/*.py.bak

realclean: clean
	-rm -rf rss.db
