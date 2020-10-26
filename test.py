#!/usr/bin/env python3
import sys, time, os, threading, unittest, pprint, subprocess

class TestCase(unittest.TestCase):
  def setUp(self):
    pass

  def test100_autodiscovery(self):
    """Test """
    import tembozapp.autodiscovery
    feed_url = tembozapp.autodiscovery.find('https://blog.majid.info/')
    assert feed_url == 'https://blog.majid.info/index.xml'

def suite():
  suite = unittest.makeSuite(TestCase, 'test')
  return suite

if __name__ == '__main__':
  unittest.main()
