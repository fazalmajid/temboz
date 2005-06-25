# This module defines a function filter() that is applied to the contents
# of a feed entry. Note: the term "filter" has nothing to do with filtering
# rules.

import re
import param

def filter(content, feed, item):
  content = filter_ads(content)
  # this seems to be caused by a bug in feedparser
  content = content.replace('<br />><br />', '<br><br>')
  return content

# strip out annoying elements
filter_re = []
for item in param.filter_re:
  assert type(item) in [str, tuple], 'filter item ' + repr(item) + \
         'must be a string or tuple suitable for re.compile'
  if type(item) == tuple:
    filter_re.append(re.compile(*item))
  elif type(item) == str:
    filter_re.append(re.compile(item))

def filter_ads(content):
  for item in filter_re:
    content = item.sub('', content)
  return content
