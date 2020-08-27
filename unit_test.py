#!/usr/local/bin/python
import sys, time, os, threading, unittest, pprint
import feedparser

class TestCase(unittest.TestCase):
  def setUp(self):
    pass

  def test100_sanitize(self):
    """Test feedparser HTML sanitizer"""
    import sanity

def suite():
  suite = unittest.makeSuite(TestCase, 'test')
  return suite

if __name__ == '__main__':
  unittest.main()
