import time, re, feedparser, codecs

#date_fmt = '%a, %d %b %Y %H:%M:%S %Z'
date_fmt = '%Y-%m-%d %H:%M:%S'

try:
  parse_date = feedparser._parse_date
except AttributeError:
  parse_date = feedparser.parse_date

def normalize(item, f):
  # get rid of RDF lossage...
  for key in ['title', 'link', 'date', 'modified', 'creator',
              'content', 'content_encoded', 'description']:
    if type(item.get(key)) == list and len(item[key]) == 1:
      item[key] = item[key][0]
    if type(item.get(key)) == dict and 'value' in item[key]:
      item[key] = item[key]['value']
  # title
  if 'title' not in item:
    item['title'] = 'Untitled'
  if type(item['title']) not in [str, unicode]:
    print 'TITLE' * 15
    import code
    from sys import exit
    code.interact(local=locals())
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
  # creator
  if 'creator' not in item or item['creator'] == 'Unknown':
    item['creator'] = 'Unknown'
    if 'creator' in f['channel']:
      item['creator'] = f['channel']['creator']
  # modified date
  if 'modified' not in item:
    item['modified'] = f['channel'].get('modified')
  # created - use modified if not available
  if 'date' not in item:
    if 'modified' in item:
      date = parse_date(item['modified'])
    else:
      date = None
  else:
    date = parse_date(item['date'])
  if not date:
    # XXX use HTTP last-modified date here
    date = time.gmtime()
  item['date'] = time.strftime(date_fmt, date)
  # finish modified date
  if item['modified']:
    modified = parse_date(item['modified'])
    # add a fudge factor within modifications are not counted as such
    # 10 minutes here
    if not modified or abs(time.mktime(modified) - time.mktime(date)) < 600:
      item['modified'] = None
    else:
      item['modified'] = time.strftime(date_fmt, modified)
  # content
  if 'content' in item:
    content = item['content']
  elif 'content_encoded' in item:
    content = item['content_encoded']
  elif 'description' in item:
    content = item['description']
  else:
    content = '<a href="' + item['link'] + '">' + item['title'] + '</a>'
  item['content'] = content
  # map unicode
  for key in ['title', 'link', 'date', 'modified', 'creator', 'content']:
    if type(item.get(key)) == unicode:
      item[key] = item[key].encode('ascii', 'xmlcharrefreplace')
  
