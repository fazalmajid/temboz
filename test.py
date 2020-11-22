#!/usr/bin/env python3
import sys, time, os, threading, unittest, pprint, subprocess
import feedparser
import tembozapp.feedfix, tembozapp.normalize, tembozapp.filters

class TestCase(unittest.TestCase):
  def setUp(self):
    pass

  def test100_autodiscovery(self):
    """Test """
    import tembozapp.autodiscovery
    feed_url = tembozapp.autodiscovery.find('https://blog.majid.info/')
    assert feed_url == 'https://blog.majid.info/index.xml'
    feed_url = tembozapp.autodiscovery.find('https://greenwald.substack.com')
    assert feed_url == 'https://greenwald.substack.com/feed/'
    feed_url = tembozapp.autodiscovery.find('https://www.calnewport.com/blog/')
    assert feed_url == 'https://www.calnewport.com/blog/feed'

  def test101_feedparser_exceptions(self):
    for fn in os.listdir('bugfeed'):
      f = open('bugfeed/' + fn, 'r')
      d = f.read()
      f.close()
      feedparser.parse(d)

  def test102_title_xss(self):
    f = open('bugfeed/boingboing', 'r')
    d = f.read()
    f.close()
    f = feedparser.parse(d)
    i = [i for i in f.entries if '>' in i.title][0]
    tembozapp.normalize.normalize(i, f, False)
    assert '>' not in i.title

  def test103_highlight(self):
    uid = 0
    for (kind, pat, s) in [
        ('title_word', 'cloud', "Sopra Steria gets £££££££s to manage cops' Oracle e-Biz suite in Oracle's cloud in Cleveland, UK"),
        ('title_word', 'gb', "Sopra Steria gets £££££££s to manage cops' Oracle e-Biz suite in Oracle's cloud in Cleveland, UK"),
    ]:
      uid += 1
      rule = tembozapp.filters.KeywordRule(
        uid, None, pat, kind)
      before = time.time()
      s2 = rule.highlight_title(s)
      after = time.time()
      assert after - before < 1.0
      assert s2 != s
      assert '<span' in s2
    
def suite():
  suite = unittest.makeSuite(TestCase, 'test')
  return suite

if __name__ == '__main__':
  unittest.main()
