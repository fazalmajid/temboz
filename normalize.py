import sys, time, re, codecs, string, traceback, md5
import feedparser, transform, util, param

# XXX TODO
#
# XXX normalize feed['title'] to quote &amp; &quot;
#
# XXX Many of these heuristics have probably been addressed by newer versions
# XXX of feedparser.py

#date_fmt = '%a, %d %b %Y %H:%M:%S %Z'
date_fmt = '%Y-%m-%d %H:%M:%S'

stop_words = ['i', 't', 'am', 'no', 'do', 's', 'my', 'don', 'm', 'on', 'get',
              'in', 'you', 'me', 'd', 've']
# list originally from: http://bll.epnet.com/help/ehost/Stop_Words.htm
stop_words += [
  'a', 'the', 'of', 'and', 'that', 'for', 'by', 'as', 'be', 'or', 'this',
  'then', 'we', 'which', 'with', 'at', 'from', 'under', 'such', 'there',
  'other', 'if', 'is', 'it', 'can', 'now', 'an', 'to', 'but', 'upon', 'where',
  'these', 'when', 'whether', 'also', 'than', 'after', 'within', 'before',
  'because', 'without', 'however', 'therefore', 'between', 'those', 'since',
  'into', 'out', 'some', 'about', 'accordingly', 'again', 'against', 'all',
  'almost', 'already', 'although', 'always', 'among', 'any', 'anyone',
  'apparently', 'are', 'arise', 'aside', 'away', 'became', 'become',
  'becomes', 'been', 'being', 'both', 'briefly', 'came', 'cannot', 'certain',
  'certainly', 'could', 'etc', 'does', 'done', 'during', 'each', 'either',
  'else', 'ever', 'every', 'further', 'gave', 'gets', 'give', 'given',
  'got', 'had', 'hardly', 'has', 'have', 'having', 'here', 'how', 'itself',
  'just', 'keep', 'kept', 'largely', 'like', 'made', 'mainly', 'make', 'many',
  'might', 'more', 'most', 'mostly', 'much', 'must', 'nearly', 'necessarily',
  'neither', 'next', 'none', 'nor', 'normally', 'not', 'noted', 'often',
  'only', 'our', 'put', 'owing', 'particularly', 'perhaps', 'please',
  'potentially', 'predominantly', 'present', 'previously', 'primarily',
  'probably', 'prompt', 'promptly', 'quickly', 'quite', 'rather', 'readily',
  'really', 'recently', 'regarding', 'regardless', 'relatively',
  'respectively', 'resulted', 'resulting', 'results', 'said', 'same', 'seem',
  'seen', 'several', 'shall', 'should', 'show', 'showed', 'shown', 'shows',
  'significantly', 'similar', 'similarly', 'slightly', 'so', 'sometime',
  'somewhat', 'soon', 'specifically', 'strongly', 'substantially',
  'successfully', 'sufficiently', 'their', 'theirs', 'them', 'they', 'though',
  'through', 'throughout', 'too', 'toward', 'unless', 'until', 'use', 'used',
  'using', 'usually', 'various', 'very', 'was', 'were', 'what', 'while', 'who',
  'whose', 'why', 'widely', 'will', 'would', 'yet' ]
stop_words = dict(zip(stop_words, [1] * len(stop_words)))
# translate to lower case, normalize whitespace
# for ease of filtering
# this needs to be a mapping as Unicode strings do not support traditional
# str.translate with a 256-length string
lc_map = {}
punct_map = {}
for c in string.whitespace:
  lc_map[ord(c)] = 32
del lc_map[32]
for c in string.punctuation + '\'':
  punct_map[ord(c)] = 32
lc_map.update(dict(zip(map(ord, string.uppercase),
                       map(ord, string.lowercase))))
# XXX need to normalize for HTML entities as well
# XXX need to strip diacritics
def lower(s):
  s = unicode(s)
  return s.translate(lc_map)

# only Python 2.4 has a built-in set type
try:
  set = set
except NameError:
  try:
    from sets import Set as set
  except ImportError:
    set = list

strip_tags_re = re.compile('<[^>]*>')
def get_words(s):
  return set([
    word for word
    in lower(unicode(strip_tags_re.sub('', unicode(s)))
             ).translate(punct_map).split()
    if word not in stop_words])
  
def normalize_all(f):
  normalize_feed(f)
  for item in f.entries:
    normalize(item, f)

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

def normalize(item, f, run_filters=True):
  # get rid of RDF lossage...
  for key in ['title', 'link', 'created', 'modified', 'author',
              'content', 'content_encoded', 'description']:
    if type(item.get(key)) == list:
      if len(item[key]) == 1:
        item[key] = item[key][0]
      else:
        candidate = [i for i in item[key] if i.get('type') == 'text/html']
        if len(candidate) == 1:
          item[key] = candidate[0]
        else:
          # XXX not really sure how to handle these cases
          print >> param.log, 'E' * 16, 'ambiguous RDF', key, item[key]
          item[key] = item[key][0]
    if isinstance(item.get(key), dict) and 'value' in item[key]:
      item[key] = item[key]['value']
  ########################################################################
  # title
  if 'title' not in item or not item['title'].strip():
    item['title'] = 'Untitled'
  # XXX for debugging
  if type(item['title']) not in [str, unicode]:
    print >> param.log, 'TITLE' * 15
    import code
    from sys import exit
    code.interact(local=locals())
  item['title_lc'] =   lower(item['title'])
  item['title_words'] =  get_words(item['title_lc'])
  ########################################################################
  # link
  #
  # The RSS 2.0 specification allows items not to have a link if the entry
  # is complete in itself
  if 'link' not in item:
    item['link'] = f['channel']['link']
    # We have to be careful not to assign a default URL as the GUID
    # otherwise only one item will ever be recorded
    if 'id' not in item:
      item['id'] = 'HASH_CONTENT'
  if type(item['link']) == unicode:
    item['link'] = str(item['link'])
  if type(item['link']) != str:
    print >> param.log, 'LINK' * 18
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
  # apply ad filters and other degunking to content
  try:
    for filter in transform.filter_list:
      content = filter.apply(content, f, item)
  except:
    util.print_stack(black_list=['item'])
  ########################################################################
  # balance tags like <b>...</b>
  # XXX should also simplify HTML entities, e.g. &eacute; -> e
  # XXX unfortunately this is an open problem with Unicode, as demonstrated
  # XXX by phishing using internationalized domain names
  content_lc = lower(content)
  # XXX this will not work correctly for <a name="..." />
  for tag in ['<b>', '<strong>', '<strike>', '<em>', '<i>', '<font ', '<a ',
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
  # we recalculate this as content may have changed due to tag rebalancing, etc
  item['content_lc'] = lower(content)
  item['content_words'] = get_words(item['content_lc'])
  item['urls'] = url_re.findall(content)
  ########################################################################
  # categories/tags
  if 'tags' in item and type(item['tags']) == list:
    item['category'] = set([t['term'].lower() for t in item['tags']])
  else:
    item['category'] = []
  ########################################################################
  # map unicode
  for key in ['title', 'link', 'created', 'modified', 'author', 'content']:
    if type(item.get(key)) == unicode:
      item[key] = item[key].encode('ascii', 'xmlcharrefreplace')
  # hash the content as the GUID if required
  if item['id'] == 'HASH_CONTENT':
    item['id']= md5.new(item['title'] + item['content']).hexdigest()
  
def escape_xml(s):
  """Escape entities for a XML target"""
  return s.decode('latin1').replace('&', '&amp;').encode('ascii', 'xmlcharrefreplace').replace("'", "&apos;").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

def escape_html(s):
  """Escape entities for a HTML target.
Differs from XML in that &apos; is defined by W3C but not implemented widely"""
  return s.decode('latin1').replace('&', '&amp;').encode('ascii', 'xmlcharrefreplace').replace("'", "&#39;").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
