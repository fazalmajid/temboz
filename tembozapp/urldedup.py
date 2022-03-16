import time, bisect
from . import param, dbop

urls = []

with dbop.db() as db:
  before = time.time()
  print('loading existing URLs', file=param.activity)
  c = db.execute("select item_link from fm_items")
  
  urls = set(row[0] for row in c)
  print('URL loading', len(urls), 'URLs done in', time.time() - before,
        file=param.activity)
  before = time.time()
  urls = list(urls)
  urls.sort()
  print('sort done in', time.time() - before, file=param.activity)

def add(url):
  i = bisect.bisect_left(urls, url)
  # do not insert a duplicate
  if i < len(urls) and urls[i] == url:
    return
  urls.insert(i, url)

def rename(old, new):
  i = bisect.bisect_left(urls, old)
  if i < len(urls) and urls[i] == old:
    urls[i] = new
    urls.sort()

def exists(url):
  i = bisect.bisect_left(urls, url)
  # match if there is an existing superstring of the URL
  return i < len(urls) and url in urls[i]
