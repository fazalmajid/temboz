PAGES= 		view error opml feeds temboz_css rules catch_up
DATE:sh=	date +'%Y-%m-%d'

JSMIN=		jsmin

all: changelog

init:
	@if [ `hostname` != "mordac" ]; then true; else echo "Will not run make init on mordac"; false; fi
	-rm -f rss.db
	sqlite3 rss.db < tembozapp/ddl.sql > /dev/null
	temboz --import me.opml
	temboz --refresh

sync:
	-mv feedparser.py feedparser.old
	wget http://feedparser.googlecode.com/svn/trunk/feedparser/feedparser.py

JUI=	spool/jquery-ui/*
sync-js:
	../src/scripts/vcheck --verbose -d --file etc/vcheck
	(cd spool; wget -N http://malsup.github.io/jquery.form.js)
	(cd spool; wget -N https://raw.githubusercontent.com/jeresig/jquery.hotkeys/master/jquery.hotkeys.js)
	(cd spool; wget -N https://unpkg.com/dexie@latest/dist/dexie.js)
	(cd spool; wget -N https://raw.githubusercontent.com/janl/mustache.js/master/mustache.js)
#	(cd spool; wget -N https://unpkg.com/colcade/colcade.js)

js: $(JUI)/external/jquery/jquery*.js spool/jquery.form.js $(JUI)/jquery-ui.js spool/jquery.hotkeys.meta.js tembozapp/static/specific.js #spool/dexie.js
	cat $^ \
	| $(JSMIN) > tembozapp/static/temboz.js
	cp spool/mustache.js tembozapp/static
	#./temboz --kill

changelog:
	cvs2cl.pl --tags -g -q

opml:
	wget -c https://majid.info/temboz/temboz.opml
	mv temboz.opml me.opml

docker:
	docker build -t fazalmajid/temboz .

docker-run:
	docker run -p 9999:9999 -v `pwd`:/temboz/data fazalmajid/temboz

sdist:
	-rm -f dist/*
	python3 setup.py sdist

pypi: sdist
	twine upload dist/*

distclean:
	-rm -f core *.pyc *~ pages/*~ *.old pages/*.py pages/*.pyc ChangeLog*
	-find . -name .\#\* -exec rm {} \;
	-find . -name .\#~ -exec rm {} \;
	-rm -f pages/*~

clean: distclean
	-rm -f pages/*.py pages/*.pyc pages/*.pyo pages/*.py.bak *.js

realclean: clean
	-rm -rf rss.db
