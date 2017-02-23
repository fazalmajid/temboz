# The Temboz feed reader

## Introduction

Temboz is a web-based RSS/Atom aggregator and feed reader that focuses on saving you time by letting you filter out articles you are not interested in.

It is inspired by FeedOnFeeds (web-based personal aggregator), Google News (two column layout) and TiVo (thumbs up and down).

## Features

* Two-column user interface for better readability and information density. Automatic reflow using CSS.
* Information Hunter-gatherer user interface: items flagged with a “Thumbs down” disappear immediately off the screen (using Dynamic HTML), making room for new articles.
* Extensive filtering capabilities:
  * By keyword or phrase
  * By tag
  * using Python expressions
* Ratings system for articles
* Share articles you flagged as “Thumbs Up” via Facebook or as an Atom feed
* Built-in web server.
* Ad filtering
* Multithreaded, download feeds in parallel.

## History

I have been using Temboz as my feed reader since 2004. I currently have over 500 feeds subscribed to, and my filtering rules get rid of around 1/3 of the incoming firehose of information.

## Screen shots

![Reader UI](https://majid.info/blog/wp-content/uploads/2004/03/t1.gif)

The first screen shot shows the article reading interface, using a two-column layout. Clicking on the “Thumbs down” icon makes the article disappear, bringing a new one in its place (if available). Clicking on the “Thumbs up” icon highlights it in yellow and flags it as interesting in the database.

![Feed summary](https://majid.info/blog/wp-content/uploads/2004/03/t2.gif)

The feed summary page shows statistics on feeds, starting with feeds with unread articles, then by alphabetical order. Feeds can be sorted based on other metrics. You have the option of “catching up” with a feed (marking all the articles as read). Feeds with errors are highlighted in red (not shown). The default sort order is by feed signal-to-noise ratio.

![Feed etails](https://majid.info/blog/wp-content/uploads/2004/03/t4.gif)

Clicking on the “details” link for a feed brings this page, which allows you to change title or feed URL, and shows the RSS or Atom fields accessible for filtering.

Feeds can be filtered by keyword, phrase, tag, author or using Python expressions.

![Filtering rules](https://majid.info/blog/wp-content/uploads/2004/03/t3.gif)

## Known bugs

You can check outstanding bug reports, change requests and more on the [GitHub issue tracker](https://github.com/fazalmajid/temboz/issues).

## Installation

You will need Python 2.7 installed on your machine.

(more complete installations with pip and virtualenv to follow)

## Credits

Temboz is written in Python, and leverages Mark Pilgrim’s Ultra-liberal feed parser, SQLite, Flask.

## Post scriptum

The name “Temboz” is a reference to Malima Temboz, “The mountain that walks”, an elephant whose tormented spirit is the object of [Mike Resnick’s](http://mikeresnick.com/) excellent SF novel, [Ivory](http://www.penguinrandomhouse.com/books/231473/ivory-by-mike-resnick/9781591025467).
