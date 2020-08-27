# this module defines classes that can be used to massage the content of an
# article, mostly to remove gunk like ads
from __future__ import print_function
import sys, re, requests, sqlite3
from . import param, util, dbop

class Filter:
  """Virtual class with the interface for all degunking filters"""
  def apply(self, content, feed, item):
    raise NotImplementedError

class Re(Filter):
  """Strip text, or rewrite a substitution for it, using regular expressions
  regex: regex to search for in article text
  flags: re compilation flags
  sub: optional substitution. The default just removes the offending match
       instead of rewriting it
  iterate: keep reiterating the process until no more matches are found
  """
  def __init__(self, regex, flags=0, sub='', iterate=False):
    self.re = re.compile(regex, flags)
    self.sub = sub
    self.iterate = iterate
  def apply(self, content, *args, **kwargs):
    content, matches = self.re.subn(self.sub, content)
    while self.iterate and matches:
      content, matches = self.re.subn(self.sub, content)
    return content

class ReUrl(Filter):
  """Find an alternative item link by either rewriting the article link, and/or
  searching for one in the contents (the URL is searched first, then contents.
  This is useful to skip summary pages and go directly to full contents
  url: substitution to use as the article link (can use backreferences like \1)
  regex_url: regex to search for in original article link
  regex_content: regex to search for in the article content
                 (only first match matters)
  flags: flags for regex compilation
  """
  def __init__(self, url, regex_url=None, regex_content=None, flags=0):
    self.url = url
    if regex_content:
      self.re_content = re.compile(regex_content, flags)
    else:
      self.re_content= None
    if regex_url:
      self.re_url = re.compile(regex_url, flags)
    else:
      self.re_url= None
  def apply(self, content, *args, **kwargs):
    item = args[1]
    if self.re_url:
      m = self.re_url.search(item['link'])
      if m:
        url = m.expand(self.url)
        item = args[1]
        item['link'] = url
        return content
    if self.re_content:
      m = self.re_content.search(content)
      if m:
        url = m.expand(self.url)
        item = args[1]
        item['link'] = url
    return content

class ReTitle(Filter):
  """Find an alternative item title
  title: substitution to use as the title (can use backreferences like \1)
  regex: regex to search for in the article content (only first match matters)
  flags: flags for regex compilation
  """
  def __init__(self, title, regex, flags=0):
    self.title = title
    self.re_content = re.compile(regex, flags)
  def apply(self, content, *args, **kwargs):
    item = args[1]
    if not item['title'] or item['title'] == 'Untitled':
      item = args[1]
      m = self.re_content.search(content)
      if m:
        title = m.expand(self.title).strip()
        if title:
          item['title'] = title
    return content

class UseFirstLink(Filter):
  """Use the first link in the body as the article link.
  Originally for the Daily Python URL feed, where the item link in the feed
  is the (useless) anchor to that item on the page, rather than the article
  itself.
  """
  url_re = re.compile('(?:href|src)="([^"]*)"', re.IGNORECASE)
  def __init__(self, prefix):
    self.prefix = prefix
  def apply(self, content, *args, **kwargs):
    item = args[1]
    if item['link'].startswith(self.prefix):
      urls = self.url_re.findall(content)
      if len(urls):
        item['link'] = urls[0]
    return content

class Dereference(Filter):
  """Dereference the item link and use a regex to find a better link. Useful
  for those annoying sites that try to force you to visit them first for banner
  impressions (e.g. Digg).
  The regex should include one group, used to extract the URL, If the regex
  fails to match, the link is unchanged, so you can be as tight as you want.
  """
  url_re = re.compile('(?:href|src)="([^"]*)"', re.IGNORECASE)
  def __init__(self, link_substr, regex):
    self.link_substr = link_substr
    self.re = re.compile(regex)
  def apply(self, content, *args, **kwargs):
    item = args[1]
    if self.link_substr in item['link']:
      try:
        # check if this item has not already been loaded before
        guid = item['id']
        with dbop.db() as db:
          c = db.cursor()
          c.execute("select item_link from fm_items where item_guid=?",
                    [guid])
          link = c.fetchone()
          c.close()
          if link:
            print('not dereferencing', guid, '->', link[0], file=param.log)
            item['link'] = link[0]
            return content
          # we haven't seen this article before, buck up and load it
          deref = requests.get(item['link'],
                               timeout=param.http_timeout).content
          m = self.re.search(deref)
          if m and m.groups():
            item['link'] = m.groups()[0]
      except:
        util.print_stack()
    return content
