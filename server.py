#!/usr/local/bin/python
import sys, os, stat, logging, base64, time, imp, gzip, traceback, pprint, csv
import threading, BaseHTTPServer, SocketServer, cStringIO, urlparse, urllib
import flask, sqlite3, string
import param, update, filters, util, normalize, dbop, singleton

# HTTP header to force caching
no_expire = [
  'Expires: Thu, 31 Dec 2037 23:55:55 GMT',
  'Cache-Control: max_age=2592000'
]

########################################################################

whitelist = {'/opml'}
class AuthWrapper:
  """HTTP Basic Authentication WSGI middleware for Pageserver"""
  def __init__(self, application):
    self.application = application

  def __call__(self, environ, start_response):
    url = environ['PATH_INFO'].rstrip('/')
    if url in whitelist or url.startswith('/static/'):
      return self.application(environ, start_response)
    auth = environ.get('HTTP_AUTHORIZATION')
    auth_login = None
    if auth and auth.startswith('Basic '):
      auth = base64.decodestring(auth[6:]).split(':')
      if len(auth) == 2:
        login, passwd = auth
        if login in param.auth_dict and param.auth_dict[login] == passwd:
          auth_login = login
    if not auth_login:
      start_response('401 Authentication Required',
                     [('WWW-Authenticate', 'Basic realm="Temboz"'),
                      ('Content-Type', 'text/html')])
      return '<h1>HTTP 401 Authentication required</h1>'
    return self.application(environ, start_response)

app = flask.Flask(__name__)
app.wsgi_app = AuthWrapper(app.wsgi_app)
app.debug = getattr(param, 'debug', False)
if not app.debug:
  # this setting interferes with Flask debug
  socket.setdefaulttimeout(10)
#app.jinja_options = {'extensions': ['jinja2.ext.do']}
app.jinja_env.trim_blocks=True
app.jinja_env.lstrip_blocks=True

from singleton import db

def change_param(*arg, **kwargs):
  parts = urlparse.urlparse(flask.request.full_path)
  parts = list(parts)
  param = urlparse.parse_qs(parts[4])
  param.update(kwargs)
  parts[4] = urllib.urlencode(param, True)
  return urlparse.urlunparse(tuple(parts))

def since(delta_t):
  if not delta_t:
    return 'never'
  delta_t = float(delta_t)
  if delta_t < 2.0/24:
    return str(int(delta_t * 24.0 * 60.0)) + ' minutes ago'
  elif delta_t < 1.0:
    return str(int(delta_t * 24.0)) + ' hours ago'
  elif delta_t < 2.0:
    return 'one day ago'
  elif delta_t < 3.0:
    return str(int(delta_t)) + ' days ago'
  else:
    return time.strftime('%Y-%m-%d',
                         time.localtime(time.time() - 86400 * delta_t))

# validate parameter names to guard against XSS attacks
valid_chars = set(string.letters + string.digits + '_')
def regurgitate_except(*exclude):
  """Regurgitate query string parameters as <input type="hidden"> fields
    to help maintain context in self-submitting forms"""
  opts = {}
  for k in flask.request.form:
    opts[k] = flask.request.form[k]
  return '\n'.join('<input type="hidden" name="%s" value="%s">'
                   % (name, urllib.quote_plus(value.encode('utf-8')))
                   for (name, value) in opts.iteritems()
                   if set(name).issubset(valid_chars)
                   and name not in ('referer', 'headers')
                   and name not in exclude)

@app.route("/")
@app.route("/view")
def view(): 
  # Query-string parameters for this page
  #   show
  #   feed_uid
  #   search
  #   where_clause
  #
  # What items to use
  #   unread:   unread articles (default)
  #   up:       articles already flagged interesting
  #   down:     articles already flagged uninteresting
  #   filtered: filtered out articles
  #   mylos:    read-only view, e.g. http://www.majid.info/mylos/temboz.html
  with dbop.db() as c:
    filters.load_rules(c)
    show = flask.request.args.get('show', 'unread')
    i = update.ratings_dict.get(show, 1)
    show = update.ratings[i][0]
    item_desc = update.ratings[i][1]
    where = update.ratings[i][3]
    sort = flask.request.args.get('sort', 'seen')
    i = update.sorts_dict.get(sort, 1)
    sort = update.sorts[i][0]
    sort_desc = update.sorts[i][1]
    order_by = update.sorts[i][3]
    # optimizations for mobile devices
    mobile = bool(flask.request.args.get('mobile', False))
    # SQL options
    params = []
    # filter by filter rule ID
    if show == 'filtered':
      try:
        params.append(int(flask.request.args['rule_uid']))
        where += ' and item_rule_uid=?'
      except:
        pass
    # filter by uid range
    try:
      params.append(int(flask.request.args['min']))
      where += ' and item_uid >= ?'
    except:
      pass
    try:
      params.append(int(flask.request.args['max']))
      where += ' and item_uid <= ?'
    except:
      pass
    # Optionally restrict view to a single feed
    feed_uid = None
    try:
      feed_uid = int(flask.request.args['feed_uid'])
      params.append(feed_uid)
      where +=  ' and item_feed_uid=?'
    except:
      pass
    # Crude search functionality
    search = flask.request.args.get('search')
    if search:
      search = search.lower()
      search_in = flask.request.args.get('search_in', 'title')
      search_where = 'item_title' if search_in == 'title' else 'item_content'
      where += ' and lower(%s) like ?' % search_where
      if type(search) == unicode:
        # XXX vulnerable to SQL injection attack
        params.append('%%%s%%' % search.encode('ascii', 'xmlcharrefreplace'))
      else:
        params.append('%%%s%%' % search)
      # Support for arbitrary where clauses in the view script. Not directly
      # accessible from the UI
      extra_where = flask.request.args.get('where_clause')
      if extra_where:
        # XXX vulnerable to SQL injection attack
        where += ' and %s' % extra_where
    # Preliminary support for offsets to read more than overload_threshold
    # articles, not fully implemented yet
    try:
      offset = int(flask.request.args['offset'])
    except:
      offset = 0
    ratings_list = ''.join(
      '<li><a href="%s">%s</a></li>' % (change_param(show=rating_name),
                                        rating_desc)
      for (rating_name, rating_desc, discard, discard) in update.ratings)
    sort_list = ''.join(
      '<li><a href="%s">%s</a></li>' % (change_param(sort=sort_name),
                                        sort_desc)
      for (sort_name, sort_desc, discard, discard) in update.sorts)
    # fetch and format items
    tag_dict, rows = dbop.view_sql(c, where, order_by, params,
                                   param.overload_threshold)
    items = []
    for row in rows:
      (uid, creator, title, link, content, loaded, created, rated,
       delta_created, rating, filtered_by, feed_uid, feed_title, feed_html,
       feed_xml, feed_snr) = row
      # redirect = '/redirect/%d' % uid
      redirect = link
      since_when = since(delta_created)
      creator = creator.replace('"', '\'')
      if rating == -2:
        if filtered_by:
          rule = filters.Rule.registry.get(filtered_by)
          if rule:
            title = rule.highlight_title(title)
            content = rule.highlight_content(content)
          elif filtered_by == 0:
            content = '%s<br><p>Filtered by feed-specific Python rule</p>' \
                      % content
      if uid in tag_dict or (creator and (creator != 'Unknown')):
        # XXX should probably escape the Unicode here
        tag_info = ' '.join('<span class="item tag">%s</span>' % t
                            for t in sorted(tag_dict.get(uid, [])))
        if creator and creator != 'Unknown':
          tag_info = '%s<span class="author tag">%s</span>' \
                     % (tag_info, creator)
        tag_info = '<div class="tag_info" id="tags_%s">' % uid \
                   + tag_info + '</div>'
        tag_call = '<a href="javascript:toggle_tags(%s);">tags</a>' % uid
      else:
        tag_info = ''
        tag_call = '(no tags)'
      items.append({
        'uid': uid,
        'since_when': since_when,
        'creator': creator,
        'loaded': loaded,
        'feed_uid': feed_uid,
        'title': title,
        'feed_html': feed_html,
        'content': content,
        'tag_info': tag_info,
        'tag_call': tag_call,
        'redirect': redirect,
        'feed_title': feed_title,
      })

    return flask.render_template('view.html', show=show, item_desc=item_desc,
                                 feed_uid=feed_uid, ratings_list=ratings_list,
                                 sort_desc=sort_desc, sort_list=sort_list,
                                 items=items,
                                 overload_threshold=param.overload_threshold)

@app.route("/xmlfeedback/<op>/<rand>/<arg>")
def ajax(op, rand, arg):
  item_uid = arg.split('.')[0]
  # for safety, these operations should be idempotent
  if op in ['promote', 'demote', 'basic', 'yappi']:
    if op != 'yappi':
      update.set_rating(int(item_uid), {
        'demote': -1,
        'basic': 0,
        'promote': 1
      }[op])
      return '<?xml version="1.0"?><nothing />'
    else:
      import yappi
      assert arg in ['start', 'stop', 'clear_stats']
      getattr(yappi, arg)()
  return '<?xml version="1.0"?><nothing />'
  
@app.route("/robots.txt")
def robots():
  return ('User-agent: *\nDisallow: /\n', 200, {'Content-Type': 'text/plain'})

@app.route("/favicon.ico")
@app.route("/api/favicon.ico")
@app.route("/apple-touch-icon.png")
@app.route("/api/apple-touch-icon.png")
def favicon():
  return ('No favicon\n', 404, {'Content-Type': 'text/plain'})

def rule_tabset(feed_uid=None):

    return flask.render_template(
      'feed.html', filters=filters,
      len=len, max=max, **locals()
    )

@app.template_filter('rule_lines')
def rule_lines(text):
  return max(4, filters.rule_lines(text))
  
@app.route("/feed/<int:feed_uid>")
@app.route("/feed/<int:feed_uid>/<op>")
def feed_info(feed_uid, op=None):
  # operations
  if op:
    if op == 'Activate':
      status = 0
      update.set_status(feed_uid, status)
    elif op == 'Suspend':
      status = 1
      update.set_status(feed_uid, status)
    elif op == 'Private':
      private = 1
      update.update_feed_private(feed_uid, private)
    elif op == 'Public':
      private = 0
      update.update_feed_private(feed_uid, private)
    elif op == 'Dupcheck':
      dupcheck = 1
      update.update_feed_dupcheck(feed_uid, dupcheck)
    elif op == 'NoDupcheck':
      dupcheck = 0
      update.update_feed_dupcheck(feed_uid, dupcheck)
    elif op == 'Exempt':
      exempt = 1
      update.update_feed_exempt(feed_uid, exempt)
    elif op == 'Reinstate':
      exempt = 0
      update.update_feed_exempt(feed_uid, exempt)
  with dbop.db() as c:
    # Get feed statistics
    row = dbop.feed_info_sql(c, feed_uid).fetchone()
    (feed_title, feed_desc, feed_filter, feed_html, feed_xml, feed_pubxml,
     delta_t, interesting, unread, uninteresting, filtered, total, status,
     private, exempt, dupcheck, feed_errors) = row
    feed_pubxml = feed_pubxml or ''
    feed_filter = feed_filter or ''
    since_when = since(delta_t)
    unread = int(unread)
    interesting = int(interesting)
    uninteresting = int(uninteresting)
    filtered = int(filtered)
    total = int(total)
    if interesting + uninteresting > 0:
      ratio = interesting * 100 / (interesting + uninteresting)
    else:
      ratio = 0
      assert interesting + uninteresting + unread + filtered == total, \
        feed_title
      uninteresting = total - unread - filtered - interesting
      if feed_filter is None:
        feed_filter = ''
    # Change feed title/html/desc/filter if requested
    notices = []
    if flask.request.method == 'POST':
      if flask.request.form.feed_title \
         and flask.request.form.feed_title != feed_title:
        feed_title = flask.request.form.feed_title
        update.update_feed_title(feed_uid, feed_title)
        notices.append('<p>Feed title updated successfully.</p>')
      if flask.request.form.feed_html \
         and flask.request.form.feed_html != feed_html:
        feed_html = flask.request.form.feed_html
        update.update_feed_html(feed_uid, feed_html)
        notices.append('<p>Feed HTML link updated successfully.</p>')
      if flask.request.form.feed_desc \
         and flask.request.form.feed_desc != feed_desc:
        feed_desc = flask.request.form.feed_desc
        update.update_feed_desc(feed_uid, feed_desc)
        notices.append('<p>Feed description updated successfully.</p>')
      if flask.request.form.feed_filter \
         and flask.request.form.feed_filter != feed_filter:
        feed_filter = flask.request.form.feed_filter
        update.update_feed_filter(feed_uid, feed_filter)
        notices.append('<p>Feed filter updated successfully.</p>')
      if flask.request.form.feed_pubxml \
         and flask.request.form.feed_pubxml != feed_pubxml:
        feed_pubxml = flask.request.form.feed_pubxml
        update.update_feed_pubxml(feed_uid, feed_pubxml)
        notices.append('<p>Feed public XML link updated successfully.</p>')
      # Change feed URL if requested
      if flask.request.args.get('refresh') == '1' \
         or (flask.request.form.get(feed_xml)
             and flask.request.form.feed_xml != feed_xml):
        try:
          num_added, num_filtered = update.update_feed_xml(
            feed_uid, flask.request.form.feed_xml)
          unread += num_added
          filtered += num_filtered
          feed_errors = 0
          notices.append('<p>Feed refreshed successfully.</p>')
          if status == 1:
            status = 0
            update.set_status(feed_uid, status)
            notices.append('<p>Feed reactivated</p>')
          if num_added > 0:
            notices.append("""<p>%d new unread articles.&nbsp;&nbsp;
      <a href="view?feed_uid=%d">view articles now</a>&nbsp;&nbsp;
      <a href="catch_up?feed_uid=%d">catch up</a></p>"""
                           % (unread, feed_uid, feed_uid))
        except update.ParseError:
          notices.append('<p><b>Connection or parse error in attempting to'
                         + 'subscribe to</b> %s, check URL</p>' % feed_xml)
        except update.FeedAlreadyExists:
          notices.append('<p>The feed %s ' % feed_xml
                         + 'is already assigned to another feed,'
                         + 'check for duplicates.</p>')
        except update.UnknownError, e:
          notices.append('<p>Unknown error:<p>\n<pre>%s</pre>\n' % e.args[0])
    feed_public = None
    hidden = regurgitate_except()
    # Display feed flags with option to change it
    if status == 0:
      status_text = 'Active'
      status_change_op = 'Suspend'
    elif status == 1:
      status_text = 'Suspended'
      status_change_op = 'Activate'
    else:
      status_text = 'Unknown'
      status_change_op = 'Activate'
    if private == 0:
      private_text = 'Public'
      private_change_op = 'Private'
    elif private == 1:
      private_text = 'Private'
      private_change_op = 'Public'
    else:
      private_text = 'Unknown'
      private_change_op = 'Private'
    if exempt == 0:
      exempt_text = 'Not exempt'
      exempt_change_op = 'Exempt'
    elif exempt == 1:
      exempt_text = 'Exempt'
      exempt_change_op = 'Reinstate'
    else:
      exempt_text = 'Unknown'
      exempt_change_op = 'Exempt'
    # Get top rules
    top_rules = dbop.top_rules(c, feed_uid)
    feed_rules = dbop.rules(c, feed_uid)
    
    return flask.render_template(
      'feed.html', filters=filters,
      len=len, max=max, **locals()
    )

@app.route("/feeds")
def feeds(): 
  sort_key = flask.request.form.get('sort', '(unread > 0) DESC, snr')
  if sort_key == 'feed_title':
    sort_key = 'lower(feed_title)'
  order = flask.request.form.get('order', 'DESC')
  with dbop.db() as db:
    cursor = db.cursor()
    cursor.execute("""select feed_uid, feed_title, feed_html, feed_xml,
    last_modified, interesting, unread, uninteresting, filtered, total,
    snr, feed_status, feed_private, feed_exempt, feed_errors,
    feed_filter notnull
    from v_feeds_snr order by feed_status ASC, """ \
    + sort_key + ' ' + order + """, lower(feed_title)""")
    rows = cursor.fetchall()
    sum_unread      = sum(int(row['unread']) for row in rows)
    sum_filtered    = sum(int(row['filtered']) for row in rows)
    sum_interesting = sum(int(row['interesting']) for row in rows)
    sum_total       = sum(int(row['total']) for row in rows)
    return flask.render_template('feeds.html',
                                 since=since, int=int, repr=repr,
                                 **locals())

def run():
  # force loading of the database so we don't have to wait an hour to detect
  # a database format issue
  c = db.cursor()
  update.load_settings(db, c)
  c.close()
  
  logging.getLogger().setLevel(logging.INFO)
  # start Flask
  app.run(host=getattr(param, 'bind_address', 'localhost'),
          port=param.port,
          threaded=True)
