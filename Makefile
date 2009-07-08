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
	wget http://feedparser.googlecode.com/svn/trunk/feedparser/feedparser.py

JUI=	spool/jquery-ui/development-bundle/ui
sync-js:
	vcheck --verbose -d --file etc/vcheck
	(cd spool; wget -N http://jqueryjs.googlecode.com/svn/trunk/plugins/form/jquery.form.js)
js:
	cat $(JUI)/../jquery-[0-9]*.js spool/jquery.form.js $(JUI)/ui.core.js  $(JUI)/ui.dialog.js $(JUI)/ui.tabs.js spool/superfish-*[0-9]/js/superfish.js | jsmin > rsrc/temboz.js
	./temboz --kill
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
	cp -r pages images etc tiny_mce temboz-$(VERSION)
	(cd temboz-$(VERSION); mv param.py param.py.sample; mv transform.py transform.py.sample; find . -name \*.pyc -exec rm {} \;; find . -name \*.pyo -exec rm {} \;; find pages -name \*.py -exec rm {} \;)
	-rm -f temboz-$(VERSION)/etc/.cvsignore
	-rm -rf temboz-$(VERSION)/pages/CVS temboz-$(VERSION)/images/CVS
	-rm -rf temboz-$(VERSION)/etc/CVS
	# expurgate password
	sed -e 's/auth_dict.=.*/auth_dict = {"login": "password"}/g' param.py > temboz-$(VERSION)/param.py
	gtar zcvf temboz-$(TAR_VERSION).tar.gz temboz-$(VERSION)
	zip -9r temboz-$(TAR_VERSION).zip temboz-$(VERSION)
	-rm -rf temboz-$(VERSION)
	-mv temboz-$(TAR_VERSION).tar.gz ../mylos/data/stories/2004/03/29
	-mv temboz-$(TAR_VERSION).zip ../mylos/data/stories/2004/03/29

dist: disttar
	-$${EDITOR} ../mylos/data/stories/2004/03/29/temboz.html

distclean:
	-rm -f core *.pyc *~ pages/*~ *.old pages/*.py pages/*.pyc ChangeLog*
	-find . -name .\#\* -exec rm {} \;
	-find . -name .\#~ -exec rm {} \;
	-rm -f pages/*~

clean: distclean
	-rm -rf temboz-$(VERSION) temboz-$(VERSION).tar.gz
	-rm -f pages/*.py pages/*.pyc pages/*.pyo pages/*.py.bak *.js

realclean: clean
	-rm -rf rss.db
