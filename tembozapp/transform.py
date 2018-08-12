# filtering regular expressions, used to strip out annoyances like ads,
# web bugs and the like from feeds
import re
import tembozapp.degunk as degunk

# uncomment this if you have made changes to the degunk module
# reload(degunk)

filter_list = [
  # don't mess with breaks
  degunk.Re('(<br\s+[^>]*>)', 0, '<br>'),
  # Blegs
  degunk.Re('<a href="http://www.bloglines.com/sub/.*?</a>'),
  degunk.Re('<a href="http://del.icio.us/post.*?</a>'),
  degunk.Re('<a href="http://digg.com/submit.*?</a>'),
  degunk.Re('<a href="http://www.furl.net/storeIt.jsp.*?</a>'),
  degunk.Re('<a href="http://ma.gnolia.com/bookmarklet/add.*?</a>'),
  degunk.Re('<a href="http://www.propeller.com/submit.*?</a>'),
  degunk.Re('<a href="http://reddit.com/submit.*?</a>'),
  degunk.Re('<a href="http://www.sphere.com/search\\?q=sphereit.*?</a>'),
  degunk.Re('<a href="http://www.stumbleupon.com/submit.*?</a>'),
  degunk.Re('<a href="http://tailrank.com/share/.*?</a>'),
  degunk.Re('<a href="http://technorati.com/faves\\?add.*?</a>'),
  degunk.Re('<a href="http://www.feedburner.com/fb/a/emailFlare.*?</a>'),
  degunk.Re('<a href="http://slashdot.org/bookmark.pl.*?</a>'),
  degunk.Re('<a href="http://www.facebook.com/sharer?.php.*?</a>'),
  degunk.Re('<a href="http://www.google.com/bookmarks/mark.*?</a>'),
  degunk.Re('<a href="http://blinklist.com.*?</a>'),
  degunk.Re('<a href="http://del.irio.us.*?</a>'),
  degunk.Re('<a href="http://www.kaboodle.com.*?</a>'),
  degunk.Re('<a href="http://www.newsvine.com.*?</a>'),
  degunk.Re('<p class="addtoany_.*?</p>', re.MULTILINE + re.DOTALL),
  degunk.Re('<a[^>]*href="[^"]*addtoany.com.*?</a>', re.MULTILINE + re.DOTALL),
  degunk.Re('<div class="social_bookmark">.*?</div>',
            re.MULTILINE + re.DOTALL),
  degunk.Re(r'<a href="http://www.pheedcontent.com.*?</a>\s*'),
  degunk.Re('<div class="zemanta.*?</div>', re.MULTILINE + re.DOTALL),
  degunk.Re('<p>Follow us on Twitter.*?</p>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  degunk.Re('<div class="tweetmeme_button".*?</div>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  degunk.Re('<p><a href="[^"]*sharethis.com.*?</p>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  degunk.Re('<a href="[^">]*.tweetmeme.com.*?</a>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  degunk.Re('<a [^>]* href="http://twitter.com/home/[?]status.*?</a>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  degunk.Re('<a [^>]*feedblitz.com.*?</a>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  # Feedburner annoyances
  degunk.Re('<a href[^>]*><img src="http://feeds.feedburner[^>]*></a>'),
  degunk.Re('<p><a href="(http://feeds\\.[^"/>]*/~./)[^"]*">'
            '<img src="\\1[^>]*></a></p>'),
  degunk.Re('<img src="http://feeds.feedburner.com.*?/>'),
  degunk.Re('<div>\\s*<a href="[^"]*/~ff/.*?</div>', re.IGNORECASE + re.DOTALL),
  # web bugs dumb enough to reveal themselves
  degunk.Re('<img[^>]*width="1"[^>]*height="1"[^>]*>'),
  degunk.Re('<img[^>]*height="1"[^>]*width="1"[^>]*>'),
  degunk.Re('<img[^>]*width="0"[^>]*height="0"[^>]*>'),
  degunk.Re('<img[^>]*height="0"[^>]*width="0"[^>]*>'),
  # Google ads
  degunk.Re('(<p>)?<a[^>]*href="http://[a-z]*ads.googleadservices[^>]*>'
            '[^<>]*<img [^<>]*></a>(</p>)?', re.MULTILINE),
  degunk.Re('<a[^>]*href="http://www.google.com/ads_by_google[^>]*>[^<>]*</a>',
            re.MULTILINE),
  degunk.Re('<p><map[^>]*><area[^>]*href="http://imageads.google.*?</p>',
            re.MULTILINE),
  # Wordpress stats
  degunk.Re('<img[^>]*src="http://feeds.wordpress[^>]*>'),
  # Falk AG ads
  degunk.Re('<div><br>\s*<strong>.*?<a href="[^"]*falkag.net[^>]*>.*?</strong>'
            '<br>.*?</div>', re.IGNORECASE + re.DOTALL),
  degunk.Re('<a href="[^"]*falkag.net[^>]*><img[^>]*></a>'),
  # Empty paragraphs used as spacers in front of ads
  degunk.Re('<p>&#160;</p>'),
  degunk.Re(r'<p><br />\s*</p>\s*', re.MULTILINE),
  degunk.Re(r'\s*(<br>)?<p>\s*<br>\s*</p>\s*', re.MULTILINE),
  # DoubleClick ads
  degunk.Re('<a[^>]*href="http://ad.doubleclick.net[^>]*>.*?</a>',
            re.MULTILINE),
  degunk.Re('<p>ADVERTISEMENT.*?</p>'),
  # Yahoo ads
  degunk.Re('<p class="adv">.*?</p>'),
  # Commindo ads
  degunk.Re('<div.*<img[^>]*commindo-media.*?</div>',
            re.MULTILINE + re.DOTALL),
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
  # Engadget ads
  degunk.Re('<hr /><p>SPONSORED BY.*?</p>\s*', re.MULTILINE),
  degunk.Re('<p.*?originally appeared on.*?terms for use of feeds.*?</p>',
            re.MULTILINE),
  # Gawker cross-shilling
  degunk.Re('&nbsp;<br><a href=[^>]*>Comment on this post</a>\s*<br>Related.*',
            re.IGNORECASE + re.DOTALL),
  degunk.Re('<div class="feedflare">.*?</div>', re.IGNORECASE + re.DOTALL),
  # Le Figaro cross-shilling
  degunk.Re('<div class="mf-related"><p>Articles en rapport.*</div>',
            re.IGNORECASE + re.DOTALL),
  # Pheedo ads
  degunk.Re('<div style="font-size: xx-small; color: gray; padding-bottom:'
            '0.5em;">Presented By:</div>[^<>]*<div><a href="http://ads.pheedo'
            '.*?</div>.*?</div>',
            re.MULTILINE + re.DOTALL),
  degunk.Re('<a[^>]*href="http://[^">]*pheedo.com.*?</a>',
            re.MULTILINE + re.DOTALL),
  degunk.Re('<img[^>]*src="http://[^">]*pheedo.com.*?>',
            re.MULTILINE + re.DOTALL),
  # Broken Pheedo links for IEEE Spectrum
  degunk.ReUrl(url=r'http://pheedo.com\1',
               regex_url=r'http://www.pheedo.com(.*)'),
  # Triggit ads
  degunk.Re('(<br>)*<img[^>]*triggit.com.*?>', re.MULTILINE + re.DOTALL),
  # Web bugs
  degunk.Re('<img[^>]*quantserve.com.*?>', re.MULTILINE + re.DOTALL),
  degunk.Re('<img [^>]*invitemedia.com[^>]*>',
            re.MULTILINE + re.DOTALL + re.IGNORECASE),
  # Mediafed ads
  degunk.Re('<br><a[^>]* href="?http://[^"]*.feedsportal.com.*?</a>',
            re.MULTILINE + re.DOTALL),
  # IDFuel URLs should point to full article, not teaser
  degunk.ReUrl(url=r'http://www.idfuel.com/index.php?p=\1&more=1',
               regex_url=r'http://www.idfuel.com/index.php\?p=([0-9]*)'),
  # Strip The Register redirection that causes link_already() to fail
  degunk.ReUrl(
    url=r'\1', regex_url=r'http://go.theregister.com/feed/(http://.*)'),
  # Same for I Cringely
  degunk.ReUrl(
  url=r'http://www.pbs.org/cringely/\1',
  regex_url=r'http://www.pbs.org/cringely/rss1/redir/cringely/(.*)'),
  # Register ads
  degunk.Re('<strong>Advertisement</strong><br>'),
  degunk.Re('<p><a[^>]*href="http://whitepapers.theregister.co.uk.*?</p>',
            re.MULTILINE),
  # Inquirer blegging
  degunk.Re('<div class="mf-viral">.*</div>'),
  # Feediz ads
  degunk.Re('<p>.*?feediz.com.*?</p>', re.MULTILINE + re.DOTALL),
  degunk.Re('<a [^>]*feediz.com.*?</a>', re.MULTILINE + re.DOTALL),
  # Salon ads
  degunk.Re('<p><a href="http://feeds.salon.com/~a[^>]*><img '
            '[^>]*></a></p><img[^>]*>'),
  # RWW ads
  degunk.Re('<p align="right" class="ad">.*?</p>'),
  # bypass Digg
  degunk.Dereference('digg.com', '<h3 id="title1"><a href="([^"]*)"'),
  # DoubleClick ads
  degunk.Re('<a href="http://[^"]*doubleclick.*?</a>',
            re.MULTILINE + re.DOTALL),
  # If I want to share, I can do it myself, thanks
  degunk.Re('<p class="akst_link">.*?</p>', re.MULTILINE + re.DOTALL),
  # Daily Python URL should link to actual articles, not to itself
  degunk.UseFirstLink('http://www.pythonware.com/daily/'),
  degunk.ReTitle('\\1', '<div class="description">.*?<a href=.*?>(.*?)</a>',
                 re.MULTILINE + re.DOTALL),
  # also broken
  degunk.UseFirstLink('http://evanmiller.org/'),
  # Inquirer clutter
  degunk.Re('<p><small>[^<>]*<a href="http://www.theinquirer.net[^<>]*><i>'
            '[^<>]*Read the full article.*', re.MULTILINE + re.DOTALL),
  degunk.Re('<p><small>[^<>]*<a href="http://www.theinquirer.net.*?<i>',
            re.MULTILINE),
  # List apart T-shirt shilling
  degunk.Re('<p><em><strong>Hide Your Shame:</strong> The A List Apart Store'
            '.*?</p>', re.MULTILINE + re.DOTALL),
  # Other misc shilling
  degunk.Re('<p>.*<a href="http://www.beyondsecurity.com.*?</p>',
            re.MULTILINE + re.DOTALL),
  degunk.Re('<fieldset class="zemanta-related">.*?</ul>',
            re.MULTILINE + re.DOTALL),
  # possibly caused by bugs in feedparser
  degunk.Re('<br>[.>]<br>', 0, '<br>', iterate=True),
  # unwarranted multiple empty lines
  degunk.Re('<br>\s*(<br>\s*)+', 0, '<br>'),
  degunk.Re('<p>&nbsp;</p>'),
  degunk.Re('<p [^>]*></p>'),
  degunk.Re('<p>-</p>'),
  degunk.Re('<span[^>]*></span>', 0, '', iterate=True),
  # junk
  degunk.Re('<strong></strong>', 0, ''),
  # unwarranted final empty lines
  degunk.Re('(<br>\s*)+$'),
  # leftover from blegs or ads
  degunk.Re('-\s+(-\s+)+'),
  # GigaOM annoyances
  degunk.Re(r'<img[^>]*src="http://stats.wordpress.com.*?>'),
  degunk.Re(r'\s*<hr[^>]*>\s*<p>\s*<a href="http://t.gigaom.com/.*?</p>',
            re.MULTILINE + re.DOTALL),
  degunk.Re(r'<hr\s?/?>\s*<a href="http://events.gigaom.com/.*</a>',
            re.MULTILINE + re.DOTALL),
  degunk.Re(r'<hr\s?/?>\s*<a href="http://pro.gigaom.com/.*</a>',
            re.MULTILINE + re.DOTALL),
  degunk.Re(r'\s*<hr[^>]*>\s*<p>\s*<a href="http://gigaom.com/sponsor.*?</p>',
            re.MULTILINE + re.DOTALL),
  degunk.Re(r'\s*<hr[^>]*>\s*<p>\s*<a href="http://ads.gigaom.com.*?</p>',
            re.MULTILINE + re.DOTALL),
  # Guardian Related sidebar
  degunk.Re(r'<div class="related" style="float.*?</div>',
            re.MULTILINE + re.DOTALL),
  # PopSci Related sidebar
  degunk.Re(r'<div class="relatedinfo".*?</div>', re.MULTILINE + re.DOTALL),
  # Ars Technica
  degunk.Re(r'<a [^>]* title="Click here to continue reading.*?</a>',
            re.MULTILINE + re.DOTALL),
  degunk.Re('<a href="http://arstechnica.com[^>]*>[^<>]*'
            '<img [^>]*brief_icons.*?</a>',
            re.MULTILINE + re.DOTALL),
  # Coding Horror
  degunk.Re(r'<table>.*?\[advertisement\].*?</table>',
            re.MULTILINE + re.DOTALL),
  # Fooducate
  degunk.Re(r'<p><span[^>]*><strong>Get Fooducated.*?</p>',
            re.MULTILINE + re.DOTALL),
  degunk.Re(r'<p>[^>]*<a href="http://alpha.fooducate.com.*?</p>',
            re.MULTILINE + re.DOTALL),
  # ReadWriteWeb ads
  degunk.Re(r'<p align="right"><em>Sponsor</em><br>.*?</p>',
            re.MULTILINE + re.DOTALL),
  # Laughing Squid
  degunk.Re('<p><hr />\s*<p>\\s*<a href="http://laughingsquid.us/">'
            '.*?Laughing Squid Web Hosting</a>.</p></p>',
            re.MULTILINE + re.DOTALL),
  # FeedBlitz
  degunk.Re('<table.*?feedblitz.com.*?</table>',
            re.MULTILINE + re.DOTALL),
  # Use m.xkcd.com instead of desktop xkcd to get the alt text
  degunk.ReUrl(url=r'http://m.xkcd.com\1',
               regex_url=r'http://xkcd.com(.*)'),
  # Medium
  degunk.Re('<figure.*?https://cdn-images-1.medium.com/max/700/1*PZjwR1Nbluff5IMI6Y1T6g@2x.png.*?</figure>',
            re.MULTILINE + re.DOTALL),
  degunk.Re('<p>.*?on Medium, where people are continuing the conversation by highlighting and responding to this story.*?/p>',
            re.MULTILINE + re.DOTALL),
  # AnandTech
  degunk.Re('<p align=center>'
            '<a href="http://dynamic[^"]*.anandtech.com/www/delivery/'
            '.*?</[ap]>',
            re.MULTILINE + re.DOTALL),
  degunk.Re('<p align=center>'
            '<a href=\'http://dynamic[^\']*.anandtech.com/www/delivery/'
            '.*?</[ap]>',
            re.MULTILINE + re.DOTALL),
  ]
