# this module defines classes that can be used to massage the content of an
# article, mostly to remove gunk like ads

import re

class Filter:
  """Virtual class with the interface for all degunking filters"""
  def apply(self, content, feed, item):
    raise NotImplementedError

class Re(Filter):
  def __init__(self, regex, flags=0, sub='', iterate=False):
    self.re = re.compile(regex, flags)
    self.sub = sub
    self.iterate = iterate
  def apply(self, content, *args, **kwargs):
    content, matches = self.re.subn(self.sub, content)
    while self.iterate and matches:
      content, matches = self.re.subn(self.sub, content)
    return content
