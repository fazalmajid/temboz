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
