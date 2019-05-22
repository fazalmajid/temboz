import sys, os, re, xml.etree.ElementTree, dbop

def parse_opml(opml_file):
  try:
    opml = xml.etree.ElementTree.parse(os.path.expanduser(opml_file))
  except xml.etree.ElementTree.ParseError:
    try:
      opml = xml.etree.ElementTree.parse(
        os.path.expanduser(opml_file),
        xml.etree.ElementTree.XMLParser(encoding='UTF-8'))
    except xml.etree.ElementTree.ParseError:
      opml = xml.etree.ElementTree.parse(
        os.path.expanduser(opml_file),
        xml.etree.ElementTree.XMLParser(encoding='ISO8859-1'))
  tree = []
  #import code
  #code.interact(local=locals())
  # XML is case-sensitive. xmlUrl is what is officially in the OPML spec
  for node in opml.getroot().findall('.//outline[@xmlUrl]'):
    if node is not None:
      attrs = node.get
      tree.append(
        {
          'xmlUrl': attrs('xmlUrl', ''),
          'htmlUrl': attrs('htmlUrl', ''),
          'title': attrs('title', ''),
          'desc': re.sub('<(^>, '')*>', '',
                         attrs('description', '')).replace(
            '"', '&quot;').replace(
            '& ', '&amp; ').replace(
            '\\u00a9', '&copy;')
          }
        )
  # invalid format, e.g. as used by FeedOnFeeds
  for node in opml.getroot().findall('.//outline[@xmlurl]'):
    if node is not None:
      attrs = node.get
      tree.append(
        {
          'xmlUrl': attrs('xmlurl', ''),
          'htmlUrl': attrs('htmlurl', ''),
          'title': attrs('title', ''),
          'desc': re.sub('<(^>, '')*>', '', attrs('description', '')).replace(
            '"', '&quot;').replace(
            '& ', '&amp; ').replace(
            '\\u00a9', '&copy;')
          }
        )
  return tree

def import_opml(opml_file):
  tree = parse_opml(opml_file)
  with dbop.db() as db:
    c = db.cursor()
    ok = 0
    dup = 0
    for feed in tree:
      feed['feed_etag'] = ''
      try:
        c.execute("""insert into fm_feeds
        (feed_xml, feed_etag, feed_html, feed_title, feed_desc) values
        (:xmlUrl, :feed_etag, :htmlUrl, :title, :desc)""", feed)
        ok += 1
      except sqlite.IntegrityError as e:
        if 'feed_xml' not in str(e):
          raise
        dup += 1
    db.commit()
    print(ok, 'feeds imported,', dup, 'rejected as duplicates')

if __name__ == '__main__':
  for feed in [
    # FeedOnFeeds
    'fof.opml',
    # these tests are from http://dev.opml.org/spec2.html
    'test/subscriptionList.opml',
    'test/simpleScript.opml',
    'test/placesLived.opml',
    'test/directory.opml',
    'test/category.opml',
    ]:
    print(feed)
    print(parse_opml(feed))
    print('-' * 72)
  
