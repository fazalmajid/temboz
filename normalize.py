import sys, time, re, feedparser, codecs

# XXX TODO
#
# XXX normalize feed['title'] to quote &amp; &quot;
#
# XXX Many of these heuristics have probably been addressed by newer versions
# XXX of feedparser.py

#date_fmt = '%a, %d %b %Y %H:%M:%S %Z'
date_fmt = '%Y-%m-%d %H:%M:%S'

def normalize_feed(f):
  if 'description' not in f['channel']:
    f['channel']['description'] = f['channel'].get('title', '')

# Often, broken RSS writers will not handle daylight savings time correctly
# and use a timezone that is off by one hour. For instance, in the US/Pacific
# time zone:
# February 3, 2004, 5:30PM is 2004-02-03T17:30:00-08:00 (standard time)
# August 3, 2004, 5:30PM US/Pacific is 2004-08-03T17:30:00-07:00 (DST)
# but broken implementations will incorrectly write:
# 2004-08-03T17:30:00-08:00 in the second case
# There is no real good way to ward against this, but if the created or
# modified date is in the future, we are clearly in this situation and
# substract one hour to correct for this bug
def fix_date(date_tuple):
  if not date_tuple:
    return date_tuple
  if date_tuple > time.gmtime():
    # feedparser's parsed date tuple has no DST indication, we need to force it
    # because there is no UTC equivalent of mktime()
    date_tuple = date_tuple[:-1] + (-1,)
    date_tuple = time.localtime(time.mktime(date_tuple) - 3600)
    # if it is still in the future, the implementation is hopelessly broken,
    # truncate it to the present
    if date_tuple > time.gmtime():
      return time.gmtime()
    else:
      return date_tuple
  else:
    return date_tuple

def normalize(item, f):
  # get rid of RDF lossage...
  for key in ['title', 'link', 'created', 'modified', 'author',
              'content', 'content_encoded', 'description']:
    if type(item.get(key)) == list and len(item[key]) == 1:
      item[key] = item[key][0]
    if isinstance(item.get(key), dict) and 'value' in item[key]:
      item[key] = item[key]['value']
  ########################################################################
  # title
  if 'title' not in item:
    item['title'] = 'Untitled'
  # XXX for debugging
  if type(item['title']) not in [str, unicode]:
    print 'TITLE' * 15
    import code
    from sys import exit
    code.interact(local=locals())
  item['title_lc'] =   item['title'].lower()
  ########################################################################
  # link
  if 'link' not in item:
    print 'E' * 16, 'no link in ', item
    item['link'] = f['channel']['link']
  if type(item['link']) == unicode:
    item['link'] = str(item['link'])
  if type(item['link']) != str:
    print 'LINK' * 18
    import code
    from sys import exit
    code.interact(local=locals())
  ########################################################################
  # creator
  if 'author' not in item or item['author'] == 'Unknown':
    item['author'] = 'Unknown'
    if 'author' in f['channel']:
      item['author'] = f['channel']['author']
  ########################################################################
  # created amd modified dates
  if 'modified' not in item:
    item['modified'] = f['channel'].get('modified')
  # created - use modified if not available
  if 'created' not in item:
    if 'modified_parsed' in item:
      created = item['modified_parsed']
    else:
      created = None
  else:
    created = item['created_parsed']
  if not created:
    # XXX use HTTP last-modified date here
    created = time.gmtime()
  created = fix_date(created)
  item['created'] = time.strftime(date_fmt, created)
  # finish modified date
  if 'modified_parsed' in item and item['modified_parsed']:
    modified = fix_date(item['modified_parsed'])
    # add a fudge factor time window within which modifications are not
    # counted as such, 10 minutes here
    if not modified or abs(time.mktime(modified) - time.mktime(created)) < 600:
      item['modified'] = None
    else:
      item['modified'] = time.strftime(date_fmt, modified)
  else:
    item['modified'] = None
  ########################################################################
  # content
  if 'content' in item:
    content = item['content']
  elif 'content_encoded' in item:
    content = item['content_encoded']
  elif 'description' in item:
    content = item['description']
  else:
    content = '<a href="' + item['link'] + '">' + item['title'] + '</a>'
  ########################################################################
  # balance tags like <b>...</b>
  content_lc = content.lower()
  # XXX this will not work correctly for <a name="..." />
  for tag in ['<b>', '<strong>', '<em>', '<i>', '<font ', '<a ',
              '<small>', '<big>', '<cite>', '<blockquote>', '<pre>',
              '<sub>', '<sup>', '<tt>', '<ul>', '<ol>',
              '<div>', '<div ', '<span>', '<span ']:
    end_tag = '</' + tag[1:]
    if '>' not in end_tag:
      end_tag = end_tag .strip() + '>'
    imbalance = content_lc.count(tag) - content_lc.count(end_tag)
    if imbalance > 0:
      content += end_tag * imbalance
  item['content'] = content
  item['content_lc'] = content.lower()
  ########################################################################
  # map unicode
  for key in ['title', 'link', 'created', 'modified', 'author', 'content']:
    if type(item.get(key)) == unicode:
      item[key] = item[key].encode('ascii', 'xmlcharrefreplace')
  
