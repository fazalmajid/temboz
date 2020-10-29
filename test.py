#!/usr/bin/env python3
import sys, time, os, threading, unittest, pprint, subprocess
import feedparser
import tembozapp.feedfix

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

  def test101_feedparser_exceptions(self):
    for fn in os.listdir('bugfeed'):
      f = open('bugfeed/' + fn, 'r')
      d = f.read()
      f.close()
      feedparser.parse(d)

def suite():
  suite = unittest.makeSuite(TestCase, 'test')
  return suite

if __name__ == '__main__':
  unittest.main()
