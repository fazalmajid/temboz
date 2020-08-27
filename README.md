# The Temboz feed reader

## Introduction

Temboz is a web-based RSS/Atom aggregator and feed reader that focuses on saving you time by letting you filter out articles you are not interested in.

It is inspired by FeedOnFeeds (web-based personal aggregator), Google News (two column layout) and TiVo (thumbs up and down).

## Features

* Two-column user interface for better readability and information density. Automatic reflow using CSS.
* Information Hunter-gatherer user interface: items flagged with a "Thumbs down" disappear immediately off the screen (using Dynamic HTML), making room for new articles.
* Extensive filtering capabilities:
  * By keyword or phrase
  * By tag
  * using Python expressions
* Ratings system for articles
* Share articles you flagged as "Thumbs Up" via Facebook or as an Atom feed
* Built-in web server.
* Ad filtering
* Multithreaded, download feeds in parallel.

## History

I have been using Temboz as my feed reader since 2004. I currently have over 500 feeds subscribed to, and my filtering rules get rid of around 1/3 of the incoming firehose of information.

## Screen shots

![Reader UI](https://temboz.com/view.png)

The home page is the article reading interface, using a two-column layout. Clicking on the "Thumbs down" icon makes the article disappear, bringing a new one in its place (if available). Clicking on the "Thumbs up" icon highlights it in yellow and flags it as interesting in the database.

![Feed summary](https://temboz.com/feeds.png)

The feed summary page shows statistics on feeds, starting with feeds with unread articles, then by alphabetical order. Feeds can be sorted based on other metrics. You have the option of "catching up" with a feed (marking all the articles as read). Feeds with errors are highlighted in red (not shown). The default sort order is by feed signal-to-noise ratio.

![Feed etails](https://temboz.com/feed.png)

Clicking on the "details" link for a feed brings up this page, which allows you to change title or feed URL, and shows the RSS or Atom fields accessible for filtering.

![Filtering rules](https://temboz.com/filters.png)

Feeds can be filtered by keyword, phrase, tag, author or using Python expressions. Filtering out junk pop culture makes for tremendous time savings.

## Known bugs

You can check outstanding bug reports, change requests and more on the [GitHub issue tracker](https://github.com/fazalmajid/temboz/issues).

## Installation

* You will need Python 3.8 installed on your machine, and a reasonably recent version of SQLite, ideally with the json1 and fts5 extensions enabled for optimum performance
* If you do not have `pip`, install it by running `python -m ensurepip` (you may need to do this as root depending on how your Python installation is set up, or use a system package manager like `apt-get`).
* If you do not have virtualenv installed, install it using `pip install virtualenv` (or use a package manager if required).
* Create a directory and virtualenv to run Temboz, in this case `tembozdir`: `virtualenv tembozdir`
* `cd tembozdir`
  * If you are a bash/ksh user: `. bin/activate`
  * If you are a tcsh/csh user: `source bin/activate.csh`
* Install Temboz in the virtualenv: `pip install temboz`
* When you run Temboz for the first time, it will prompt you for the network address/port it should listen on, and your login/password: `./bin/temboz`
* Optionally, you can import an OPML subscription file if you have one: `./bin/temboz --import foo.opml`
* If you imported subscriptions, you can trigger a manual refresh: `./bin/temboz --refresh`
* You can now start the Temboz server: `./bin/temboz --server`

## Keeping informed

I would highly recommend you subscribe to Temboz' [RSS feed](https://blog.majid.info/categories/temboz/index.xml) to be notified of security releases and other major announcements. It's less than one post a year, I promise...

## Credits

Temboz is written in Python, and leverages Mark Pilgrim’s Ultra-liberal feed parser, SQLite, Flask.

## Post scriptum

The name "Temboz" is a reference to Malima Temboz, "The mountain that walks", an elephant whose tormented spirit is the object of [Mike Resnick’s](http://mikeresnick.com/) excellent SF novel, [Ivory](http://www.penguinrandomhouse.com/books/231473/ivory-by-mike-resnick/9781591025467).
