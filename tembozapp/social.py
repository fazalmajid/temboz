#!/usr/bin/env python
import logging, requests, json, urlparse
import param, normalize, util

class ExpiredToken(Exception):
  pass

def fb_post(token, msg, url):
  print >> param.activity, 'FACEBOOK', msg, url
  msg = normalize.decode_entities(msg).encode('utf-8')
  fb_url = 'https://graph.facebook.com/me/feed'
  data = dict(urlparse.parse_qsl('access_token=' + token))
  data['message'] = msg
  data['link'] = url
  try:
    req = requests.post(fb_url, data=data)
    out = json.loads(req.content)
    if 'id' not in out:
      raise ValueError(req.content)
    print >> param.activity, 'FACEBOOK OUT', url, out
    return out
  except (ValueError, requests.exceptions.RequestException) as e:
    print >> param.log, '$' * 72
    print >> param.log, 'FACEBOOK API ERROR'
    print >> param.log, 'FB_URL = %r' % fb_url
    print >> param.log, 'FB_DATA = %r' % data
    try:
      info = e.read()
    except:
      info = repr(e)
    print >> param.log, 'INFO = %r' % info
    print >> param.log, '$' * 72
    if 'access token' in info:
      raise ExpiredToken
    raise

def fb_feed(token):
  fb_url = 'https://graph.facebook.com/me/home'
  data = dict(urlparse.parse_qsl('access_token=' + token))
  try:
    req = requests.get(fb_url, params=data)
    return req.content
  except requests.exceptions.RequestException as e:
    print >> param.log, '$' * 72
    print >> param.log, 'FACEBOOK API ERROR'
    print >> param.log, 'TOKEN = %r' % token
    print >> param.log, 'INFO = %r' % e
    print >> param.log, '$' * 72
    raise
