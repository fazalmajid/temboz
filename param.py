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

# garbage collection - articles flagged as "uninteresting" will have their
# content automatically dumped after this interval (but not their title or
# permalink) to make room. If this parameter is set to None or False, this
# garbage-collection will not occur
garbage_contents = 7
# garbage_contents = None

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
