import sys, time, re, codecs, string, traceback
import feedparser, transform, util

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

url_re = re.compile('(?:href|src)="([^"]*)"', re.IGNORECASE)

punct_map = {}
for c in string.punctuation:
  punct_map[ord(c)] = 32

def normalize(item, f):
  # get rid of RDF lossage...
  for key in ['title', 'link', 'created', 'modified', 'author',
              'content', 'content_encoded', 'description']:
    if type(item.get(key)) == list:
      if len(item[key]) == 1:
        item[key] = item[key][0]
      else:
        # XXX not really sure how to handle these cases
        print 'E' * 16, 'ambiguous RDF', item[key]
        item[key] = item[key][0]
    if isinstance(item.get(key), dict) and 'value' in item[key]:
      item[key] = item[key]['value']
  ########################################################################
  # title
  if 'title' not in item or not item['title'].strip():
    item['title'] = 'Untitled'
  # XXX for debugging
  if type(item['title']) not in [str, unicode]:
    print 'TITLE' * 15
    import code
    from sys import exit
    code.interact(local=locals())
  item['title_lc'] =   item['title'].lower()
  item['title_words'] =  unicode(item['title_lc']).translate(punct_map).split()
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
  # XXX special case handling for annoying Sun/Roller malformed entries
  if 'blog.sun.com' in item['link'] or 'blog.sun.com' in item['link']:
    item['link'] = item['link'].replace(
      'blog.sun.com', 'blogs.sun.com').replace(
      'blogs.sun.com/page', 'blogs.sun.com/roller/page')
  ########################################################################
  # GUID
  if 'id' not in item:
    item['id'] = item['link']
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
    # feeds that do not have timestamps cannot be garbage-collected
    # XXX need to find a better heuristic, as high-volume sites such as
    # XXX The Guardian, CNET.com or Salon.com lack item-level timestamps
    f['oldest'] = '1970-01-01 00:00:00'
  created = fix_date(created)
  item['created'] = time.strftime(date_fmt, created)
  # keep track of the oldest item still in the feed file
  if 'oldest' not in f:
    f['oldest'] = '9999-99-99 99:99:99'
  if item['created'] < f['oldest']:
    f['oldest'] = item['created']
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
  if not content:
    content = '<a href="' + item['link'] + '">' + item['title'] + '</a>'
  # strip embedded NULs as a defensive measure
  content = content.replace('\0', '')
  # apply transforms like stripping ads
  try:
    content = transform.filter(content, f, item)
  except:
    util.print_stack()
  ########################################################################
  # balance tags like <b>...</b>
  # XXX should also simplify HTML entities, e.g. &eacute; -> e
  # XXX unfortunately this is an open problem with Unicode, as demonstrated
  # XXX by phishing using internationalized domain names
  content_lc = content.lower()
  # XXX this will not work correctly for <a name="..." />
  for tag in ['<b>', '<strong>', '<em>', '<i>', '<font ', '<a ',
              '<small>', '<big>', '<cite>', '<blockquote>', '<pre>',
              '<sub>', '<sup>', '<tt>', '<ul>', '<ol>',
              '<div>', '<div ', '<span>', '<span ',
              '<td>', '<td ', '<th>', '<th ', '<tr>', '<tr ',
              '<table>', '<table ']:
    end_tag = '</' + tag[1:]
    if '>' not in end_tag:
      end_tag = end_tag .strip() + '>'
    imbalance = content_lc.count(tag) - content_lc.count(end_tag)
    if imbalance > 0:
      content += end_tag * imbalance
  # the content might have invalid 8-bit characters.
  # Heuristic suggested by Georg Bauer
  if type(content) != unicode:
    try:
      content = content.decode('utf-8')
    except UnicodeError:
      content = content.decode('iso-8859-1')
  #
  item['content'] = content
  item['content_lc'] = content.lower()
  item['content_words'] = unicode(item['content_lc']).translate(
    punct_map).split()
  item['urls'] = url_re.findall(content)
  ########################################################################
  # map unicode
  for key in ['title', 'link', 'created', 'modified', 'author', 'content']:
    if type(item.get(key)) == unicode:
      item[key] = item[key].encode('ascii', 'xmlcharrefreplace')
  
def escape_xml(s):
  """Escape entities for a XML target"""
  return s.decode('latin1').replace('&', '&amp;').encode('ascii', 'xmlcharrefreplace').replace("'", "&apos;").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

def escape_html(s):
  """Escape entities for a HTML target.
Differs from XML in that &apos; is defined by W3C but not implemented widely"""
  return s.decode('latin1').replace('&', '&amp;').encode('ascii', 'xmlcharrefreplace').replace("'", "&#39;").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
