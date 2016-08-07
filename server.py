#!/usr/local/bin/python
# $Id: server.py,v 1.47 2010/09/07 11:59:13 majid Exp $
import sys, os, stat, logging, base64, time, imp, gzip, traceback, pprint, csv
import threading, BaseHTTPServer, SocketServer, cStringIO, urlparse, urllib
import TembozTemplate, param, update, filters, util, normalize, singleton

# work around incompatibility between html5lib and Cheetah ImportHooks
import __builtin__, Cheetah.ImportManager, logging
sys_import = __builtin__.__import__
def fix_import(self, *args, **kwargs):
  try:
    return self.saved_importHook(*args, **kwargs)
  except:
    #logging.exception('Cheetah import hook error')
    return sys_import(*args, **kwargs)
Cheetah.ImportManager.ImportManager.saved_importHook = Cheetah.ImportManager.ImportManager.importHook
Cheetah.ImportManager.ImportManager.importHook = fix_import
# add the Cheetah template directory to the import path
import Cheetah.ImportHooks
Cheetah.ImportHooks.install()
try:
  tmpl_dir = os.path.dirname(sys.modules['__main__'].__file__)
except:
  tmpl_dir = os.getcwd()
if tmpl_dir:
  mod_dir = tmpl_dir + os.sep + 'modules'
  tmpl_dir += os.sep + 'pages'
else:
  tmpl_dir = 'pages'
  mod_dir = 'modules'
try:
  os.mkdir(mod_dir)
except OSError:
  pass
Cheetah.ImportHooks.setCacheDir(mod_dir)
sys.path.append(mod_dir)
sys.path.append(tmpl_dir)

class Server(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  pass

# HTTP header to force caching
no_expire = [
  'Expires: Thu, 31 Dec 2037 23:55:55 GMT',
  'Cache-Control: max_age=2592000'
]

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  tmpl_cache = {}
  dep_cache = {}
  load_t = {}
  def version_string(self):
    """Return the server software version string."""
    return param.user_agent
  
  def log_message(self, *args):
    pass

  def read_mime_query_list(self, mimeinfo):
    """Magic to return attributes and attachments during a POST
    Keyword arguments:
    mimeinfo -- String of headers
    """
    stream = cStringIO.StringIO()
    stream.write(mimeinfo)
    stream.seek(0)
    attr_list = []
    attach_list = []
    msg = mimetools.Message(stream)
    msgtype = msg.gettype()
    params = msg.getplist()
    data = cStringIO.StringIO()
    file = multifile.MultiFile(stream)
    file.push(msg.getparam('boundary'))
    while file.next():
      submsg = mimetools.Message(file)
      try:  
        data = cStringIO.StringIO()
        mimetools.decode(file, data, submsg.getencoding())
      except ValueError:   
        continue
      headerinfo = {}
      for i in submsg.getheader('content-disposition').split('; '):
        try:
          (n, v) = i.split('=', 2)
          if v[0] == '"':
            v = v[1:]
            if v[-1] == '"':
              v = v[0:-1]
          headerinfo[n] = v
        except: 
          pass
      realval = data.getvalue()[0:-2]
      try:
        attach_list.append((
          headerinfo['name'], \
          submsg.gettype(), \
          headerinfo['filename'], \
          realval \
        ))
      except KeyError:
        attr_list.append((headerinfo['name'], realval))
    file.pop()
    return (attr_list, attach_list)

  def browser_output(self, response, ct, output, http_headers=None):
    """Compose an output to the browser.

    Keyword arguments:
    response -- Numeric Response code
    ct -- Content-Type to use, defaults to text/html if None
    output -- Output body
    http_headers -- Optional list of HTTP headers

    """
    self.output_send_response(response)
    if not http_headers:
      http_headers = list()
    #text / html page use utf 8 output
    #if ct:
    #  self.output_send_header('Content-Type', ct)
    if not ct or ct.startswith('text/html'):
      self.output_send_header('Content-Type',"text/html; charset=utf-8")
    else:
      self.output_send_header('Content-Type', ct)
    # gzip compression
    if ct and ct.startswith('text') and len(output) > 1500 \
           and 'accept-encoding' in self.headers.dict \
           and 'gzip' in self.headers.dict['accept-encoding'] \
           and 'user-agent' in self.headers.dict \
           and 'MSIE' not in self.headers.dict['user-agent'] \
           and False \
           and 'gondwana.majid.org:8443' not in self.headers['host']:
      http_headers.append('Content-Encoding: gzip')
      gzbuf = cStringIO.StringIO()
      gzfile = gzip.GzipFile(fileobj=gzbuf, mode='wb', compresslevel=9)
      try:
        gzfile.write(output)
      except UnicodeEncodeError:
        gzfile.write(output.encode('ascii', 'xmlcharrefreplace'))
      gzfile.close()
      output = gzbuf.getvalue()
      http_headers.append('Content-Length: %d' % len(output))
      
    for i in http_headers:
      mname, mvalue = i.split(': ', 1)
      self.output_send_header(mname, mvalue)
    self.output_end_headers()
    self.output_print(output)

  def output_print(self, msg):
    """Print to the outfile (self.wfile), but ignore IO errors"""
    try:
      print >> self.wfile, msg
    except UnicodeEncodeError:
      print >> self.wfile, msg.encode('ascii', 'xmlcharrefreplace')
    except IOError:
      pass

  def output_send_response(self, resp):
    """Run self.send_response, but ignore IO errors

    Keyword arguments:
    resp -- Numeric HTTP response

    """
    try:
      self.send_response(resp)
    except IOError:
      pass

  def output_send_header(self, n, v):
    """Run self.send_header, but ignore IO errors

    Keyword arguments:
    n -- Header name
    v -- Header value

    """
    try:
      self.send_header(n, v)
    except IOError:
      pass

  def output_end_headers(self):
    """Run self.end_headers, but ignore IO errors

    Keyword arguments:
    none

    """
    try:
      self.end_headers()
    except IOError:
      pass

  def require_auth(self, auth_dict, realm='temboz'):
    """Requires HTTP Basic Authentication"""
    if self.headers.dict.has_key('authorization'):
      if self.headers.dict['authorization'].startswith('Basic '):
        auth = base64.decodestring(
          self.headers.dict['authorization'][6:]).split(':')
        if len(auth) == 2:
          login, passwd = auth
          if login in auth_dict and auth_dict[login] == passwd:
            return login
    self.browser_output(
      401, 'text/html', """<h1>401 Authorization required</h1><p>%%s</p>
      <script language="JavaScript">document.location.href="%s";</script>""" \
      % param.unauth_page,
      ['WWW-Authenticate: Basic realm="%s"' % realm])
    return

  def init_session(self):
    self.mime_type = 'text/html'
    self.output_buffer = []
    self.host, self.port = self.client_address
    if self.headers.dict.has_key('user-agent'):
      self.user_agent = self.headers.dict['user-agent']
    else:
      self.user_agent = ''
    if self.headers.dict.has_key('referer'):
      self.referer = self.headers.dict['referer']
    else:
      self.referer = ''
    self.input = {'referer': self.referer,
                  'headers': self.headers.dict}

  def process_post_info(self):
    """Processes POST variables coming in, either standard or
    form-data.
    """
    # XXX We may want to check that content-length exists 
    # XXX or catch KeyError
    if self.headers.gettype() == 'multipart/form-data':
      mimeinfo = self.headers.__str__() + \
                 self.rfile.read(int(self.headers['content-length']))
      (query_list, self.attach_list) = self.read_mime_query_list(mimeinfo)
      self.input.update(dict(query_list))
    else:
      istr = self.rfile.read(int(self.headers['content-length']))
      for name, value in urlparse.parse_qsl(istr, 1):
        # RFC3986 is the normative reference for urlencoded strings such
        # as those sent in the default form encoding
        # application/x-www-form-urlencoded
        # RFC3986 specifies characters have to be encoded using UTF-8
        # Unfortunately some older browsers encode as ISO-8859-1 instead
        # (more likely Windows-1252), e.g. Firefox with the setting
        # network.standard-url.encode-query-utf8=false (still the case as of
        # Firefox 3.5, unfortunately), see Bugzilla bug 333859
        # We will first attempt to decode using the RFC3986 standard, and if
        # an exception is thrown, fall back to Windows-1252
        try:
          value = value.decode('UTF-8')
        except UnicodeDecodeError:
          value = value.decode('Windows-1252')
        self.input[name] = value

  def do_POST(self):
    try:
      self.init_session()
      self.process_post_info()
      self.process_request()
    except:
      raise

  def do_GET(self):
    try:
      self.init_session()
      self.process_request()
    except:
      raise

  def response(self):
    return self

  def write(self, output):
    self.output_buffer.append(output)

  def flush(self):
    # make the browser cache temboz_css, which still needs to be dynamically
    # generated for the browser because it is browser-dependent (to deal with
    # IE standards noncompliance issues)
    if self.mime_type == 'text/css':
      http_headers = no_expire
    else:
      http_headers = []
    self.browser_output(200, self.mime_type, ''.join(self.output_buffer),
                        http_headers=http_headers)

  images = {}
  for fn in [fn for fn in os.listdir('images')
             if fn.endswith('.gif') or fn.endswith('.ico')]:
    images[fn] = open('images/' + fn).read()
  rsrc = {}
  for fn in [fn for fn in os.listdir('rsrc')
             if fn.endswith('.js') and not fn.startswith('.')]:
    rsrc[fn] = open('rsrc/' + fn).read()
  def favicon(self):
    self.browser_output(200, 'image/x-icon', self.images['favicon.ico'],
                        http_headers=no_expire)
  def xml(self):
    self.browser_output(200, 'text/xml', '<?xml version="1.0"?><nothing />')

  def op_demote(self, item_uid):
    update.set_rating(item_uid, -1)
    
  def op_basic(self, item_uid):
    update.set_rating(item_uid, 0)
    
  def op_promote(self, item_uid):
    update.set_rating(item_uid, 1)

  def op_yappi(self, command):
    import yappi
    assert command in ['start', 'stop', 'clear_stats']
    getattr(yappi, command)()

  def set_mime_type(self, tmpl):
    if type(tmpl) in [list, tuple]:
      tmpl = tmpl[-1]
    tmpl = tmpl.lower()
    if tmpl.endswith('.css'):
      self.mime_type = 'text/css'
    if tmpl.endswith('_css'):
      self.mime_type = 'text/css'
    elif tmpl.endswith('.gif'):
      self.mime_type = 'image/gif'
    elif tmpl.endswith('.png'):
      self.mime_type = 'image/png'
    elif tmpl.endswith('.jpg')  or tmpl.endswith('.jpeg'):
      self.mime_type = 'image/jpeg'
    elif tmpl.endswith('.js'):
      self.mime_type = 'text/javascript'
    elif tmpl.endswith('.xml'):
      self.mime_type = 'text/xml'
    elif tmpl.endswith('.js'):
      self.mime_type = 'application-x/javascript'
    elif tmpl.endswith('.csv'):
      self.mime_type = 'application/vnd.ms-excel'
    else:
      self.mime_type = 'text/html'

  def use_template(self, tmpl, searchlist):
    """Use compiled-on-demand versions of Cheetah templates for
    speed, specially with CGI
    """
    self.set_mime_type(tmpl)
    mod = __import__(tmpl)
    tmpl = getattr(mod, tmpl)
    tmpl = tmpl(searchList=searchlist)
    tmpl.respond(trans=self)
    self.flush()

  def process_request(self):
    try:
      if self.path in ['', '/']:
        self.browser_output(301, None, 'This document has moved.',
                            ['Location: /view'])
        return
      path, query_string = urlparse.urlparse(self.path)[2:5:2]
      vars = []
      if query_string:
        # parse_qsl does not comply with RFC 3986, we have to decode UTF-8
        query_list = [(n, v.decode('UTF-8'))
                      for n, v in urlparse.parse_qsl(query_string, 1)]
        self.input.update(dict(query_list))

      if param.debug:
        logging.info((self.command, self.path, self.request_version, vars))

      if path.endswith('.gif') and path[1:] in self.images:
        self.browser_output(200, 'image/gif', self.images[path[1:]],
                            http_headers=no_expire)
        return

      if path.endswith('.js') and path[1:] in self.rsrc:
        self.browser_output(200, 'text/javascript', self.rsrc[path[1:]],
                            http_headers=no_expire)
        return

      if path.startswith('/tiny_mce'):
        # guard against attempts to subvert security using ../
        path = os.path.normpath('.' + path)
        assert path.startswith('tiny_mce')
        self.set_mime_type(path)
        self.browser_output(200, self.mime_type, open(path).read(),
                            http_headers=no_expire)
        return

      if path.count('favicon.ico') > 0:
        self.favicon()

      if path.endswith('.css'):
        path = path.replace('.css', '_css')
        tmpl = path.split('/', 1)[1].strip('/')
        self.use_template(tmpl, [self.input])

      if not self.require_auth(param.auth_dict):
        return
      
      if path.startswith('/redirect/'):
        from singleton import db
        c = db.cursor()
        item_uid = int(path[10:])
        c.execute('select item_link from fm_items where item_uid=%d'
                  % item_uid)
        redirect_url = c.fetchone()[0]
        c.close()
        self.browser_output(301, None, 'This document has moved.',
                            ['Location: ' + redirect_url])
        return

      if path.startswith('/threads'):
        frames = sys._current_frames()
        row = 0
        out = []
        if singleton.c_opened:
          out.append('<h1>Open Cursors</h1>\n')
          for curs, tb in singleton.c_opened.iteritems():
            if curs not in singleton.c_closed:
              row += 1
              if row % 2:
                color = '#ddd'
              else:
                color = 'white'
              out.append('<div style="background-color: ' + color + '">\n<pre>')
              out.append(curs.replace('<', '&lt;').replace('>', '&gt;') + '\n')
              out.append('\n'.join(tb[:-2]))
              out.append('</pre></div>\n')
        out.append('<h1>Threads</h1>\n')
        row = 0
        for thread_id, frame in sorted(frames.iteritems()):
          if thread_id == threading.currentThread()._Thread__ident:
            continue
          row += 1
          if row % 2:
            color = '#ddd'
          else:
            color = 'white'
          out.append('<div style="background-color: ' + color + '">\n<pre>')
          out.append('Thread %s (%d refs)\n'
                     % (thread_id, sys.getrefcount(frame)))
          out.append(''.join(traceback.format_stack(frame)).replace(
            '&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
          out.append('\n<hr>\n')
          out.append(pprint.pformat(frame.f_locals).replace(
            '&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
          out.append('\n</pre>\n</div>\n')
        del frames
        self.browser_output(200, 'text/html', ''.join(out))
        return

      if path.startswith('/xmlfeedback/'):
        op, item_uid = path.split('/')[2::2]
        item_uid = item_uid.split('.')[0]
        # for safety, these operations should be idempotent
        if op in ['promote', 'demote', 'basic', 'yappi']:
          if op != 'yappi':
            item_uid = int(item_uid)
          getattr(self, 'op_' + op)(item_uid)
        self.xml()
        return

      if path.startswith('/stem'):
        txt = self.input['q']
        stem = ' '.join(normalize.stem(normalize.get_words(txt)))
        self.browser_output(200, 'text/plain', stem)
        return

      if path.startswith('/add_kw_rule'):
        from singleton import db
        c = db.cursor()
        try:
          filters.add_kw_rule(db, c, **self.input)
        except:
          util.print_stack()
        db.commit()
        c.close()
        self.xml()
        return

      if path.startswith('/del_kw_rule'):
        from singleton import db
        c = db.cursor()
        try:
          filters.del_kw_rule(db, c, **self.input)
        except:
          util.print_stack()
        db.commit()
        c.close()
        self.xml()
        return

      if path.startswith('/stats'):
        from singleton import db
        c = db.cursor()
        c.execute("""select date(item_loaded) as date, count(*) as articles,
        sum(case when item_rating=1 then 1 else 0 end) as interesting,
        sum(case when item_rating=0 then 1 else 0 end) as unread,
        sum(case when item_rating=-1 then 1 else 0 end) as filtered
        from fm_items
        where item_loaded > julianday('now') - 30
        group by 1 order by 1""")
        csvfile = cStringIO.StringIO()
        out = csv.writer(csvfile, dialect='excel', delimiter=',')
        out.writerow([col[0].capitalize() for col in c.description])
        for row in c:
          out.writerow(row)
        self.browser_output(200, 'text/csv', csvfile.getvalue())
        csvfile.close()
        c.close()
        return

      if path.endswith('.css'):
        path = path.replace('.css', '_css')

      tmpl = path.split('/', 1)[1].strip('/')
      self.use_template(tmpl, [self.input])
    except TembozTemplate.Redirect, e:
      redirect_url = e.args[0]
      self.browser_output(301, None, 'This document has moved.',
                          ['Location: ' + redirect_url])
      return
    except:
      e = sys.exc_info()
      self.use_template('error', [self.input, {'e': e}])
      self.flush()
      e = None
    return

  def change_param(self, *arg, **kwargs):
    parts = urlparse.urlparse(self.path)
    parts = list(parts)
    param = urlparse.parse_qs(parts[4])
    param.update(kwargs)
    parts[4] = urllib.urlencode(param, True)
    return urlparse.urlunparse(tuple(parts))

def run():
  # force loading of the database so we don't have to wait an hour to detect
  # a database format issue
  from singleton import db
  c = db.cursor()
  update.load_settings(db, c)
  c.close()
  
  logging.getLogger().setLevel(logging.INFO)
  server = Server((getattr(param, 'bind_address', ''), param.port), Handler)
  pidfile = open('temboz.pid', 'w')
  print >> pidfile, os.getpid()
  pidfile.close()
  server.serve_forever()

class DummyRequest:
  """Emulate a BaseHTTPServer from a CGI"""
  def makefile(self, mode, size):
    if mode == 'rb':
      url = os.getenv('PATH_INFO')
      if os.getenv('QUERY_STRING'):
        url += '?' + os.getenv('QUERY_STRING')
      request = """%(method)s %(url)s %(protocol)s\n""" % {
        'method': os.getenv('REQUEST_METHOD'),
        'url': url,
        'protocol': os.getenv('SERVER_PROTOCOL'),
        }
      request += '\n'.join(['%s: %s' % (name[5:].replace('_', '-'), value)
                            for (name, value) in os.environ.iteritems()
                            if name.startswith('HTTP_')])
      cl = os.getenv('CONTENT_LENGTH')
      if cl:
        cl = int(cl)
        request += '\nContent-Length: %d\n\n%s' % (cl, sys.stdin.read(cl))
      else:
        request += '\n\n'
      f = open('/tmp/sopz', 'w')
      f.write(request)
      f.close()
      return cStringIO.StringIO(request)
    elif mode == 'wb':
      return sys.stdout

def require_auth(self, *args, **kwargs):
  return os.getenv('REMOTE_USER')

def do_cgi():
  """Implement a CGI using a BaseHTTPHandler subclass"""
  param.log = open('/dev/null', 'w')
  Handler.require_auth = require_auth
  h = Handler(DummyRequest(), ('localhost', 80), None)
