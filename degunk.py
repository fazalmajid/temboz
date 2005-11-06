# this module defines classes that can be used to massage the content of an
# article, mostly to remove gunk like ads

import sys, re

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