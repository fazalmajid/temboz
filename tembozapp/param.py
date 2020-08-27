########################################################################
#
# Parameter file for Temboz
#
########################################################################

# number of RSS feeds fetched in parallel 
feed_concurrency = 20

# Maximum number of articles shown
overload_threshold = 200

# feed polling interval in seconds
refresh_interval = 3600

# half-life of articles' contribution towards the SNR
decay = 90

# Whether "catch-up" links require user confirmation (default is yes)
catch_up_confirm = True
hard_purge_confirm = True

# automatic backups
# stream compression utility to use for backups
backup_compressor = ('gzip -9c', '.gz')
#backup_compressor = ('bzip2 -9c', '.bz2)
# number of daily backups to keep
daily_backups = 7
# at what time should the backup be made (default: between 3 and 4 AM)
backup_hour = 4

# garbage collection - articles flagged as "uninteresting" will have their
# content automatically dumped after this interval (but not their title or
# permalink) to make room. If this parameter is set to None or False, this
# garbage-collection will not occur
garbage_contents = 7
# garbage_contents = None

# after a longer period of time, the articles themselves are purged, assuming
# they are no longer in the feed files (otherwise they would reappear the next
# time the feed is loaded)
# Note: this needs to be set much higher than the healf life for SNR
garbage_items = 180
# garbage_items = None

# URL to use as the User-Agent when downloading feeds
temboz_url = 'https://www.temboz.com/'
# user agent shown when fetching the feeds
user_agent = 'Temboz (%s)' % temboz_url
def default_user_agent():
  return user_agent
import requests
requests.utils.default_user_agent = default_user_agent

# page unauthenticated users should see
# the most common case is people checking the referrer logs on their web server
unauth_page = temboz_url

# dictionary of login/password
try:
  from private import auth_dict
except:
  auth_dict = {'majid': 'sopo'}

# maximum number of errors, after this threshold is reached,
# the feed is automatically suspended. -1 to unlimit
max_errors = 1000

#debug = True
debug = False
#debug_sql = True
debug_sql = False
#profile = False

# logging
import sys, os
log_filename = 'error.log'
if '--daemon' in sys.argv:
  # if you modify mode and buffer size, see also update.py:cleanup
  # for the code that rotates this file daily
  log = open(log_filename, 'a', 0)
  os.dup2(log.fileno(), 1)
  os.dup2(log.fileno(), 2)
  activity = open('activity.log', 'a')
else:
  log = sys.stderr
  activity = sys.stderr
# redirect stout and stderr to the log file

# default timeout for HTTP requests in seconds
http_timeout = 60.0

# These settings are managed in the database and will ultimately supersede
# param.py
settings = {}
