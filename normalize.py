import time, re, feedparser

#date_fmt = '%a, %d %b %Y %H:%M:%S %Z'
date_fmt = '%Y-%m-%d %H:%M:%S'

def normalize(item, f):
  # get rid of RDF lossage...
  for key in ['title', 'link', 'date', 'modified', 'creator']:
    if type(item.get(key)) == list and len(item[key]) == 1:
      item[key] = item[key][0]
    if type(item.get(key)) == dict and 'value' in item[key]:
      item[key] = item[key]['value']
  # title
  if 'title' not in item:
    item['title'] = 'Untitled'
  if type(item['title']) != str:
    print 'ß' * 72
    import code
    from sys import exit
    code.interact(local=locals())
  # link
  if 'link' not in item:
    print 'E' * 16, item
    item['link'] = f['channel']['link']
  if type(item['link']) != str:
    print 'ø' * 72
    import code
    from sys import exit
    code.interact(local=locals())
  # creator
  if 'creator' not in item or item['creator'] == 'Unknown':
    item['creator'] = 'Unknown'
    if 'creator' in f['channel']:
      item['creator'] = f['channel']['creator']
  # date
  if 'date' not in item:
    # XXX this code should go away in final versions
    # find possible alternative date fields
    sop = [k for k in item.keys() if k not in
           ['description', 'link', 'title', 'guid', 'content_encoded',
            'links', 'creator', 'summary', 'id', 'content',
            'category', 'categories', 'comments']]
    if sop:
      print '#' * 72
      import code
      from sys import exit
      code.interact(local=locals())
    # /XXX
    # XXX use HTTP last-modified date here
    item['date'] = time.strftime(date_fmt, time.gmtime())
  else:
    date = feedparser.parse_date(item['date'])
    if not date:
      print '$' * 16, item['date']
      date = time.gmtime()
      item['date'] = time.strftime(date_fmt, time.gmtime())
    item['date'] = time.strftime(date_fmt, date)
  # modified date
  if 'modified' not in item:
    # XXX this code should go away in final versions
    # find possible alternative date fields
    sop = [k for k in item.keys() if k not in
           ['date', 'description', 'link', 'title', 'guid', 'content_encoded',
            'links', 'creator', 'summary', 'id', 'content',
            'category', 'categories', 'comments']]
    if sop:
      print '$' * 72
      import code
      from sys import exit
      code.interact(local=locals())
    # /XXX
    item['modified'] = None
  else:
    modified = feedparser.parse_date(item['modified'])
    # add a fudge factor within modifications are not counted as such
    # 10 minutes here
    if not modified or abs(time.mktime(modified) - time.mktime(date)) < 600:
      item['modified'] = None
    else:
      item['modified'] = time.strftime(date_fmt, modified)
  # content
  if 'content_encoded' in item:
    content = item['content_encoded']
  elif 'description' in item:
    content = item['description']
  else:
    # XXX take this out
    sop = [k for k in item.keys() if k not in
           ['description', 'link', 'title', 'guid', 'content_encoded',
            'links', 'creator', 'summary', 'id', 'date',
            'modified_parsed', 'date_parsed', 'modified']]
    if sop:
      print '@' * 72
      import code
      from sys import exit
      code.interact(local=locals())
    else:
      content = '<a href="' + item['link'] + '">' + item['title'] + '</a>'
  item['content'] = content
  
