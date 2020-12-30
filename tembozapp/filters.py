# handle the various type of FilteringRules
from __future__ import print_function
import time, re, textwrap, requests, html5lib
from . import normalize, param, util, dbop

rules = []
feed_rules = {}
loaded = False

def evaluate_rules(item, feed, feed_uid, exempt):
  for rule in rules * (not exempt) + feed_rules.get(feed_uid, list()):
    try:
      if rule.test(item, feed, feed_uid):
        return True, rule
    except:
      util.print_stack(['f'])
  return False, None

class Rule:
  registry = dict()
  def __init__(self, uid, expires):
    assert uid not in self.registry
    self.registry[uid] = self
    self.uid = uid
    self.expires = expires
  def __str__(self):
    return '<Rule %s>' % self.uid
  def __repr__(self):
    return self.__str__()
  def check_expires(self):
    return self.expires and time.time() > self.expires
  def highlight_title(self, html):
    return html
  def highlight_content(self, html):
    return html

class KeywordRule(Rule):
  def __init__(self, uid, expires, rule, rtype):
    Rule.__init__(self, uid, expires)
    self.target, self.match = rtype.split('_', 1)
    assert self.target in ['title', 'content']
    if self.match in ['exactword']:
      self.rule = normalize.get_words(rule)
    elif self.match in ['word', 'all']:
      self.rule = normalize.stem(normalize.get_words(rule))
    else:
      self.rule = rule
  def __str__(self):
    return '<KeywordRule %s %s %s %s>' % (self.uid, self.target, self.match,
                                          self.rule)
  def test(self, item, feed, feed_uid):
    if self.check_expires():
      return False
    if self.match in ['word', 'all']:
      suffix = '_words'
    elif self.match == 'exactword':
      suffix = '_words_exact'
    elif self.match == 'phrase_lc':
      suffix = '_lc'
    else:
      suffix = ''
    target = item[self.target + suffix]
    if self.match in ('word', 'exactword'):
      return bool(target.intersection(self.rule))
    elif self.match == 'exactword':
      return bool(target.intersection(self.rule))
    elif self.match == 'all':
      return bool(target.issuperset(self.rule))
    else:
      return self.rule in target
  def highlight(self, html):
    if type(self.rule) in [str, str]:
      return normalize.replace_first(
        html, self.rule, '<span class="filter-highlight">', '</span>')
    else:
      for word in self.rule:
        html = normalize.replace_first(
          html, word, '<span class="filter-highlight">', '</span>')
      return html
  def highlight_title(self, html):
    if self.target == 'content' \
           and self.uid > 0 and -self.uid in self.registry:
      return  self.highlight(html)
    if self.target == 'title':
      return  self.highlight(html)
    return html
  def highlight_content(self, html):
    if self.target == 'content':
      return  self.highlight(html)
    return html

class TagRule(Rule):
  def __init__(self, uid, expires, rule):
    Rule.__init__(self, uid, expires)
    self.rule = normalize.lower(rule)
  def __str__(self):
    return '<TagRule %s %s>' % (self.uid, self.rule)
  def test(self, item, feed, feed_uid):
    if self.check_expires():
      return False
    for tag in item['item_tags']:
      if self.rule == tag:
        return True
    return False
  def highlight_content(self, html):
    return '%s<br><p>Filtered for tag <span class="item tag highlighted">%s</span></p>' \
           % (html, self.rule)

class AuthorRule(Rule):
  def __init__(self, uid, expires, rule):
    Rule.__init__(self, uid, expires)
    self.rule = rule
  def __str__(self):
    return '<AuthorRule %s %s>' % (self.uid, self.rule)
  def test(self, item, feed, feed_uid):
    if self.check_expires():
      return False
    return self.rule == normalize.lower(item['author'])
  def highlight_content(self, html):
    return '%s<br><p>Filtered for author <span class="author tag highlighted">%s</span></p>' \
           % (html, self.rule)

########################################################################
# functions used inside Python rules
def link_already(url):
  with dbop.db() as db:
    print('checking for deja-vu for', url, end=' ', file=param.activity)
    c = db.execute("select count(*) from fm_items where item_link like ?",
               [url + '%'])
    l = c.fetchone()
    print(l and l[0], file=param.log)
    return l and l[0]

def link_extract(link_text, content):
  """Extract first link after link_text"""
  h = html5lib.parse(content, namespaceHTMLElements=False)
  candidates = h.findall(".//a[.='%s']" % link_text)
  if not candidates:
    return 'NOT MATCHED'
  try:
    return candidates[0].attrib['href']
  except:
    return 'NOT MATCHED'

def dereference_content(url):
  try:
    r = requests.get(url, timeout=param.http_timeout)
    return r.content
  except:
    return ''

# shades of LISP...
def curry(fn, obj):
  return lambda *args: fn(obj, *args)

# obj can be a string, list or dictionary
def any(obj, *words):
  for w in words:
    if w in obj:
      return True
  return False

def union_any(obj_list, *words):
  for w in words:
    for obj in obj_list:
      if w in obj:
        return True
  return False

########################################################################

rule_comment_re = re.compile('^#.*$', re.MULTILINE)
def normalize_rule(rule):
  """allow embedded CR/LF and comments to make for more readable rules"""
  return rule_comment_re.sub('', rule).replace(
    '\n', ' ').replace('\r', ' ').strip()

wrapper = textwrap.TextWrapper(width=80, break_long_words=False)
# XXX this relies on texwrap implementation details to prevent wrapping on
# XXX hyphens and em-dashes, only on spaces
wrapper.wordsep_re = re.compile(r'(\s+)')
def rule_lines(rule):
  "Find how many lines are needed for the rule in a word-wrapped <textarea>"
  if not rule:
    return 4
  lines = 0
  for line in rule.splitlines():
    if line.strip():
      lines += len(wrapper.wrap(line))
    else:
      lines += 1
  return lines

class PythonRule(Rule):
  def __init__(self, uid, expires, rule):
    Rule.__init__(self, uid, expires)
    self.rule = rule
    rule = normalize_rule(rule)
    self.code = compile(rule, 'rule' + repr(uid), 'eval')
  def __str__(self):
    return '<PythonRule %s %s>' % (self.uid, normalize_rule(self.rule))
  def test(self, item, feed, feed_uid):
    if self.check_expires():
      return False
    filter_dict = dict()
    for key in feed.feed:
      try:
        filter_dict['feed_' + key] = feed.feed[key]
      except KeyError:
        pass
    filter_dict.update(item)
    # for backward compatibility, see normalize.py
    filter_dict['category'] = filter_dict['item_tags']
    # used to filter echos from sites like Digg
    filter_dict['link_already'] = link_already
    filter_dict['link_extract'] = link_extract
    filter_dict['dereference_content'] = dereference_content
    # convenient shortcut functions
    filter_dict['title_any_words'] = curry(any, item['title_words'])
    filter_dict['content_any_words'] = curry(any, item['content_words'])
    filter_dict['union_any_words'] = curry(
      union_any, [item['title_words'], item['content_words']])
    filter_dict['title_any'] = curry(any, item['title'])
    filter_dict['content_any'] = curry(any, item['content'])
    filter_dict['union_any'] = curry(
      union_any, [item['title'], item['content']])
    filter_dict['title_any_lc'] = curry(any, item['title_lc'])
    filter_dict['content_any_lc'] = curry(any, item['content_lc'])
    filter_dict['union_any_lc'] = curry(
      union_any, [item['title_lc'], item['content_lc']])
    return bool(eval(self.code, filter_dict))
  def highlight_title(self, html):
    return html
  def highlight_content(self, html):
    return html + '<br><p>Filtered by Python rule %d</p>' % self.uid
    
def load_rules(c):
  global loaded, rules, feed_rules
  if loaded: return
  rules = []
  feed_rules = dict()
  try:
    try:
      for uid, rtype, rule, feed_uid, expires in \
          c.execute("""select rule_uid, rule_type, rule_text, rule_feed_uid,
          strftime('%s', rule_expires)
          from fm_rules
          where rule_expires is null or rule_expires > julianday('now')"""):
        if expires: expires = int(expires)
        if feed_uid:
          container = feed_rules.setdefault(feed_uid, list())
        else:
          container = rules
        if rtype == 'python':
          rule = PythonRule(uid, expires, rule)
          container.append(rule)
        elif rtype == 'tag':
          rule = TagRule(uid, expires, rule)
          container.append(rule)
        elif rtype == 'author':
          rule = AuthorRule(uid, expires, rule)
          container.append(rule)
        elif rtype.startswith('union_'):
          # XXX this convention of adding a second rule object with UID -uid
          # XXX is a ugly hack
          container.append(KeywordRule(
            -uid, expires, rule, rtype.replace('union_', 'title_')))
          container.append(KeywordRule(
            uid, expires, rule, rtype.replace('union_', 'content_')))
        else:
          container.append(KeywordRule(uid, expires, rule, rtype))
      for feed_uid, rule in \
          c.execute("""select feed_uid, feed_filter from fm_feeds
          where feed_filter is not null"""):
        rule = PythonRule('feed_%d' % feed_uid, None, rule)
        feed_rules.setdefault(feed_uid, list()).append(rule)
    except:
      util.print_stack()
  finally:
    loaded = True

def invalidate():
  """Invalidate the rule cache to force reloading from the database"""
  # break cyclic references
  Rule.registry.clear()
  global loaded
  loaded = False

def update_rule(db, c, uid, expires, text, delete):
  if expires == 'never':
    expires = 'NULL'
  else:
    expires = "julianday('%s')" % expires
  # check syntax
  compile(normalize_rule(text), 'web form', 'eval')
  if uid == 'new':
    c.execute("insert into fm_rules (rule_expires, rule_text) values (?, ?)",
              [expires, text])
  elif delete == 'on':
    c.execute("delete from fm_rules where rule_uid=?", [uid])
  else:
    c.execute("""update fm_rules set rule_expires=?, rule_text=?
    where rule_uid=?""", [expires, text, uid])
  db.commit()
  invalidate()

def add_kw_rule(db, c, kw=None, item_uid=None, match='word', target='title',
                feed_only=False, retroactive=False, stem=None, **kwargs):
  feed_only = bool(feed_only)
  retroactive = bool(retroactive)

  if feed_only:
    item_uid = int(item_uid)
  else:
    item_uid = None

  if match == 'word':
    kw = stem
  if not kw: return
  if match in ['author', 'tag', 'phrase_lc']:
    words = [normalize.lower(kw)]
  elif match in {'word', 'exactword'}:
    words = normalize.get_words(kw)
  elif match == 'all':
    words = [' '.join(normalize.get_words(kw))]
  elif match == 'phrase':
      words = [kw]
  else:
    return
  
  if match in ['author', 'tag']:
    rule_type = match
  else:
    rule_type = target + '_' + match

  for word in words:
    print('ADD_KW_RULES', rule_type, item_uid, word, file=param.log)
    c.execute("""insert into fm_rules (rule_type, rule_feed_uid, rule_text)
    values (?, (select item_feed_uid from fm_items where item_uid=?), ?)""",
              [rule_type, item_uid, word]);
  invalidate()

def del_kw_rule(db, c, rule_uid=None, **kwargs):
  c.execute("""update fm_items
  set item_rating=0, item_rule_uid=NULL
  where item_rule_uid=? and item_content!=''""", [rule_uid])
  c.execute('delete from fm_rules where rule_uid=?', [rule_uid])
  invalidate()

def exempt_feed_retroactive(db, c, feed_uid, **kwargs):
  """Retroactively unfilter a feed that is exempted from filtering"""
  c.execute("""update fm_items
  set item_rating=0, item_rule_uid=NULL
  where item_feed_uid=? and item_content!='' and exists (
    select rule_uid from fm_rules
    where rule_feed_uid is null and item_rule_uid=rule_uid
  )""", [feed_uid])

########################################################################
# stats
def stats(c):
  return c.execute("""select rule_uid, rule_type, rule_text,
    coalesce(rule_feed_uid, -1), feed_title,
    sum(case when item_created > julianday('now')-7 then 1 else 0 end) last_7,
    sum(case when item_created < julianday('now')-7 then 1 else 0 end) prev_7,
    min(case when item_created > julianday('now')-7
             then item_uid else 2000000000 end),
    max(case when item_created > julianday('now')-7
             then item_uid else 0 end)
  from fm_rules
  join fm_items on item_rule_uid=rule_uid
  left join fm_feeds on rule_feed_uid=feed_uid
  where item_created > julianday('now') -14
  group by 1, 2, 3, 4, 5
  order by 6 desc
  limit 100""")
