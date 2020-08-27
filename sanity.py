# essential sanity checks, do not start temboz if these fail
import sys, os.path, pprint, feedparser, bleach
import tembozapp.normalize as normalize

bugfeed = (os.path.dirname(__file__) or '.') + os.sep + 'bugfeed'
#print(__file__, bugfeed)
calmatters = open(bugfeed + os.sep + 'calmatters')
text = calmatters.read()
calmatters.close()
#import pdb
#pdb.set_trace()

f = feedparser.parse(text)
for i in f.entries:
  normalize.normalize(i, f, False)
  #pprint.pprint(i)
  assert '<script>' not in repr(i), \
    'Refusing to start Temboz because feedparser is not sanitizing properly'
