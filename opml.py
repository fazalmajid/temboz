import sys, os, re, pyRXP, sqlite

def opml_process(tree, level=0, out=[]):
  if type(tree) != tuple:
    return
  tag, attrs, children, spare = tree
  if tag == 'head':
    return
  if tag == 'body':
    level = 0
  if tag == 'outline':
    # Sharpreader
    if 'xmlUrl' in attrs:
      # skip myself
#       if 'majid.info' in attrs['xmlUrl']:
#         return
      out.append({
        'xmlUrl': attrs['xmlUrl'].replace('\'', '\'\''),
        'htmlUrl': attrs['htmlUrl'].replace('\'', '\'\''),
        'title': attrs['title'].replace('\'', '\'\''),
        'desc': re.sub('<[^>]*>', '', attrs.get('description', '')).replace(
        '"', '&quot;').replace(
        '& ', '&amp; ').replace(
        '\xa9', '&copy;').replace('\'', '\'\'')})
    # FeedOnFeeds
    elif 'xmlurl' in attrs:
      # skip myself
#       if 'majid.info' in attrs['xmlurl']:
#         return
      out.append({
        'xmlUrl': attrs['xmlurl'].replace('\'', '\'\''),
        'htmlUrl': attrs['htmlurl'].replace('\'', '\'\''),
        'title': attrs['title'].replace('\'', '\'\''),
        'desc': re.sub('<[^>]*>', '', attrs.get('description', '')).replace(
        '"', '&quot;').replace(
        '& ', '&amp; ').replace(
        '\xa9', '&copy;').replace('\'', '\'\'')})
  if children:
    for t in children:
      opml_process(t, level + 1, out)

def parse_opml(opml_file):
  opml = pyRXP.Parser().parse(open(
    os.path.expanduser(opml_file)).read())
  tree = []
  opml_process(opml, 0, tree)
  return tree

def import_opml(opml_file):
  tree = parse_opml(opml_file)
  from singleton import db
  c = db.cursor()
  ok = 0
  dup = 0
  for feed in tree:
    feed['feed_etag'] = ''
    try:
      c.execute("""insert into fm_feeds
      (feed_xml, feed_etag, feed_html, feed_title, feed_desc) values
      ('%(xmlUrl)s', '%(feed_etag)s', '%(htmlUrl)s', '%(title)s',
      '%(desc)s')""" % feed)
      ok += 1
    except sqlite.IntegrityError, e:
      if 'feed_xml' not in str(e):
        raise
      dup += 1
  db.commit()
  print ok, 'feeds imported,', dup, 'rejected as duplicates'

if __name__ == '__main__':
  #import_opml('../mylos/data/gems/sharpreader.opml')
  print parse_opml('fof.opml')
  #print parse_opml('../mylos/data/gems/sharpreader.opml')
  
