debug = True
port = 9999
temboz_url = 'http://www.majid.info/mylos/stories/2004/03/29/temboz.html'
# number of RSS feeds fetched in parallel 
feed_concurrency = 10
# Maximum number of articles shown
overload_threshold = 200
# refresh interval in seconds
refresh_interval = 3600
# user agent shown when fetching the feeds
user_agent = 'Temboz (%s)' % temboz_url
# page unauthenticated users should see
unauth_page = temboz_url
