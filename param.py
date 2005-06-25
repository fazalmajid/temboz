########################################################################
#
# Parameter file for Temboz
#
########################################################################

# TCP port to use for the web server
port = 9999

# number of RSS feeds fetched in parallel 
feed_concurrency = 10

# Maximum number of articles shown
overload_threshold = 200

# feed polling interval in seconds
refresh_interval = 3600

# Whether "catch-up" links require user confirmation (default is yes)b
catch_up_confirm = True

# automatic backups
# stream compression utility to use for backups
backup_compressor = ('gzip -9c', '.gz')
#backup_compressor = ('bzip2 -9c', '.bz2)
# number of daily backups to keep
daily_backups = 7
# at what time should the backup be made (default: between 3 and 4 AM)
backup_hour = 3

# garbage collection - articles flagged as "uninteresting" will have their
# content automatically dumped after this interval (but not their title or
# permalink) to make room. If this parameter is set to None or False, this
# garbage-collection will not occur
garbage_contents = 7
# garbage_contents = None

# after a longer period of time, the articles themselves are purges, assuming
# they are no longer in the feed files (otherwise they would reappear the next
# time the feed is loaded)
garbage_items = 180
# garbage_items = None

# URL to use as the User-Agent when downloading feeds
temboz_url = 'http://www.temboz.com/'
# user agent shown when fetching the feeds
user_agent = 'Temboz (%s)' % temboz_url

# page unauthenticated users should see
unauth_page = temboz_url

# dictionary of login/password
auth_dict = {'majid': 'sopo'}

# maximum number of errors, after this threshold is reached,
# the feed is automatically suspended. -1 to unlimit
max_errors = 100

#debug = True
debug = False

# filtering regular expressions, used to strip out annoyances like ads,
# web bugs and the like from feeds
# strip out feedburner and Google ads
import re
filter_re = [
  # Feedburner ads
  '<a href[^>]*><img src="http://feeds.feedburner[^>]*></a>',
  # Feedburner web bug
  '<img src="http://feeds.feedburner.com.*?/>',
  # Google ads
  ('<a[^>]*href="http://imageads.googleadservices[^>]*>[^<>]*<img [^<>]*></a>',
   re.MULTILINE),
  ('<a[^>]*href="http://www.google.com/ads_by_google[^>]*>[^<>]*</a>',
   re.MULTILINE),
  # Falk AG ads
  '<a href="[^"]*falkag.net[^>]*><img[^>]*></a>',
  # Empty paragraphs used as spacers in front of ads
  '<p>&#160;</p>',
  # DoubleClick ads
  ('<a[^>]*href="http://ad.doubleclick.net[^>]*>.*?</a>',
   re.MULTILINE),
  '<p>ADVERTISEMENT.*?</p>',
  # annoying forms inside posts, e.g. Russell Beattie
  ('<form.*?</form>', re.IGNORECASE + re.DOTALL),
  # annoying Weblogs Inc. footer
  ('<a href=[^>]*>Permalink</a>.*?<a [^>]*>Email this</a>.*?Comments</a>', re.IGNORECASE + re.DOTALL),
  '<h6></h6>',
  ]

# Logging, controlled by the standard Python logging module
import logging
log = logging.getLogger('Temboz')
