import urllib.parse
import requests, html5lib, feedparser
from . import param

def find(url):
  html = requests.get(url,
                      headers={'user-agent': param.user_agent},
                      timeout=param.http_timeout).content
  tree = html5lib.parse(html, namespaceHTMLElements=False)
  # base for relative URLs
  base = tree.findall('.//base')
  if base and 'href' in base[0].attrib:
    base = base[0].attrib
  else:
    base = url
  # prioritize Atom over RSS
  links = tree.findall(
    """head/link[@rel='alternate'][@type='application/atom+xml']"""
  ) + tree.findall(
    """head/link[@rel='alternate'][@type='application/rss+xml']"""
  )
  for link in links:
    attrs = link.attrib
    # most likely, if we are autodiscovering a feed, we are interested
    # in the articles, not the comments
    if 'comments' in attrs.get('href', '').strip().lower():
      continue
    if 'comments feed' in attrs.get('title', '').strip().lower():
      continue
    if 'href' in attrs:
      return urllib.parse.urljoin(base, attrs['href'])
  # no usable autodiscovery links in the meta, try some heuristics
  for suffix in [
      'feed', 'feed/', 'rss', 'atom', 'feed.xml',
      '/feed', '/feed/', '/rss', '/atom', '/feed.xml',
      'index.atom', 'index.rss', 'index.xml', 'atom.xml', 'rss.xml',
      '/index.atom', '/index.rss', '/index.xml', '/atom.xml', '/rss.xml',
      '.rss', '/.rss', '?rss=1', '?feed=rss2',
  ]:
    try:
      u = urllib.parse.urljoin(base, suffix)
      f = feedparser.parse(u)
      if 'url' in f:
        return u
    except:
      pass
    
