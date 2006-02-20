# filtering regular expressions, used to strip out annoyances like ads,
# web bugs and the like from feeds
import re, degunk

# uncomment this if you have made changes to the degunk module
# reload(degunk)

filter_list = [
  # don't mess with breaks
  degunk.Re('(<br\s+[^>]*>)', 0, '<br>'),
  # Feedburner ads
  degunk.Re('<a href[^>]*><img src="http://feeds.feedburner[^>]*></a>'),
  # Feedburner web bug
  degunk.Re('<img src="http://feeds.feedburner.com.*?/>'),
  # Google ads
  degunk.Re('<a[^>]*href="http://imageads.googleadservices[^>]*>'
            '[^<>]*<img [^<>]*></a>', re.MULTILINE),
  degunk.Re('<a[^>]*href="http://www.google.com/ads_by_google[^>]*>[^<>]*</a>',
            re.MULTILINE),
  degunk.Re('<p><map[^>]*><area[^>]*href="http://imageads.google.*?</p>',
            re.MULTILINE),
  # Falk AG ads
  degunk.Re('<div><br>\s*<strong>.*?<a href="[^"]*falkag.net[^>]*>.*?</strong>'
            '<br>.*?</div>', re.IGNORECASE + re.DOTALL),
  degunk.Re('<a href="[^"]*falkag.net[^>]*><img[^>]*></a>'),
  # Empty paragraphs used as spacers in front of ads
  degunk.Re('<p>&#160;</p>'),
  degunk.Re('<p><br />\s*</p>\s*', re.MULTILINE),
  # DoubleClick ads
  degunk.Re('<a[^>]*href="http://ad.doubleclick.net[^>]*>.*?</a>',
            re.MULTILINE),
  degunk.Re('<p>ADVERTISEMENT.*?</p>'),
  # Yahoo ads
  degunk.Re('<p class="adv">.*?</p>'),
  # annoying forms inside posts, e.g. Russell Beattie
  degunk.Re('<form.*?</form>', re.IGNORECASE + re.DOTALL),
  # Weblogs Inc, ads
  degunk.Re('<p><a[^>]*href="http://feeds.gawker.com[^>]*>[^<>]*'
            '<img [^>]*src="http://feeds.gawker.com[^<>]*></a></p>',
            re.MULTILINE),
  # annoying Weblogs Inc. footer
  degunk.Re('<h([0-9])></h\1>'),
  degunk.Re('<a href=[^>]*>Permalink</a>.*?<a [^>]*>'
            'Email this</a>.*?Comments</a>',
            re.IGNORECASE + re.DOTALL),
  degunk.Re('<p><font size="1"><hr />SPONSORED BY.*?</p>'),
  # Gawker cross-shilling
  degunk.Re('&nbsp;<br><a href=[^>]*>Comment on this post</a>\s*<br>Related.*',
            re.IGNORECASE + re.DOTALL),
  # Pheedo ads
  degunk.Re('<p><a href="http://www.pheedo.*?</p>', re.MULTILINE + re.DOTALL),
  degunk.Re('<div><a href="http://www.pheedo[^"]*">\s*'
            '<img src="http://www.pheedo.com.*?</div>',
            re.MULTILINE + re.DOTALL),
  # IDFuel URLs should point to full article, not teaser
  degunk.ReUrl(url=r'http://www.idfuel.com/index.php?p=\1&more=1',
               regex_url=r'http://www.idfuel.com/index.php\?p=([0-9]*)'),
  # Daily Python URL should link to actual articles, not to itself
  degunk.UseFirstLink('http://www.pythonware.com/daily/'),
  # possibly caused by bugs in feedparser
  degunk.Re('<br>[.>]<br>', 0, '<br>', iterate=True),
  # unwarranted multiple empty lines
  degunk.Re('<br>(<br>)+', 0, '<br>'),
  # unwarranted final empty lines
  degunk.Re('(<br>)+$'),
  ]
