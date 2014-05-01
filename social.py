#!/usr/bin/env python
import logging, urllib2
import param, normalize, util

class ExpiredToken(Exception):
  pass

def fb_post(token, msg, url):
  print >> param.activity, 'FACEBOOK', msg, url
  msg = normalize.decode_entities(msg).encode('utf-8')
  fb_url = 'https://graph.facebook.com/me/feed'
  data = 'access_token=' + token + '&message=' + urllib2.quote(msg) \
         + '&link=' + urllib2.quote(url)
  try:
    req = urllib2.urlopen(fb_url, data)
    return req.read()
  except urllib2.HTTPError as e:
    print >> param.log, '$' * 72
    print >> param.log, 'FACEBOOK API ERROR'
    print >> param.log, 'FB_URL = %r' % fb_url
    print >> param.log, 'FB_DATA = %r' % data
    info = e.read()
    print >> param.log, 'INFO = %r' % info
    print >> param.log, '$' * 72
    if 'access token' in info:
      raise ExpiredToken
    raise

def fb_feed(token):
  fb_url = 'https://graph.facebook.com/me/home?access_token=' + token
  try:
    req = urllib2.urlopen(fb_url)
    return req.read()
  except urllib2.HTTPError as e:
    print >> param.log, '$' * 72
    print >> param.log, 'FACEBOOK API ERROR'
    print >> param.log, 'FB_URL = %r' % fb_url
    print >> param.log, 'FB_DATA = %r' % data
    print >> param.log, 'INFO = %r' % e.read()
    print >> param.log, '$' * 72
    raise
