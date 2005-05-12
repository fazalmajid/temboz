# This module defines a function filter() that is applied to the contents
# of a feed entry. Note: the term "filter" has nothing to do with filtering
# rules.

import re

def filter(content, feed, item):
  content = filter_ads(content)
  # this seems to be caused by a bug in feedparser
  content = content.replace('<br />><br />', '<br><br>')
  return content

# strip out feedburner and Google ads
fb_ad_re = re.compile(
  '<a href[^>]*><img src="http://feeds.feedburner[^>]*></a>')
goog_ad_re1 = re.compile(
  '<a[^>]*href="http://imageads.googleadservices[^>]*>[^<>]*<img [^<>]*></a>',
  re.MULTILINE)
goog_ad_re2 = re.compile(
  '<a[^>]*href="http://www.google.com/ads_by_google[^>]*>[^<>]*</a>',
  re.MULTILINE)
def filter_ads(content):
  return fb_ad_re.sub('', goog_ad_re1.sub('', goog_ad_re2.sub('', content)))
