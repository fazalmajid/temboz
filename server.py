#!/usr/local/bin/python
# $Id$
import sys, os, logging, base64, time

import BaseHTTPServer, SocketServer, cgi
from Cheetah.Template import Template
import param

class Server(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  pass

class TembozTemplate(Template):
  def since(self, delta_t):
    if not delta_t:
      return 'never'
    delta_t = float(delta_t)
    if delta_t < 2.0/24:
      return str(int(delta_t * 24.0 * 60.0)) + ' minutes ago'
    elif delta_t < 1.0:
      return str(int(delta_t * 24.0)) + ' hours ago'
    elif delta_t < 3.0:
      return str(int(delta_t)) + ' days ago'
    else:
      return time.strftime('%Y-%m-%d',
                           time.localtime(time.time() - 86400 * delta_t))

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  def version_string(self):
    """Return the server software version string."""
    return param.user_agent
  
  def log_message(self, *args):
    pass

  def read_mime_query_list(self, mimeinfo):
    """Voodoo magic to return attributes and attachments during a POST

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

  def browser_output(self, response, ct, output, http_headers=[]):
    """Compose an output to the browser.

    Keyword arguments:
    response -- Numeric Response code
    ct -- Content-Type to use, defaults to text/html if None
    output -- Output body
    http_headers -- Optional list of HTTP headers

    """
    self.output_send_response(response)
    if ct:
      self.output_send_header('Content-Type', ct)
    for i in http_headers:
      mname, mvalue = i.split(': ', 1)
      self.output_send_header(mname, mvalue)
    self.output_end_headers()
    self.output_print(output)

  def output_print(self, msg):
    """Print to the outfile (self.wfile), but ignore IO errors"""
    try:
      print >> self.wfile, msg
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
    self.input = {}

  def process_post_info(self):
    """Processes POST variables coming in, either standard or form-data."""
    # XXXX: We may wantto check that content-length exists 
    # or catch KeyError as this shows up in the logs somewhat
    # often.  The question is, what we should do if this field
    # does not exist.  (fledo@kefta.com)
    if self.headers.gettype() == 'multipart/form-data':
      mimeinfo = self.headers.__str__() + \
                 self.rfile.read(int(self.headers['content-length']))
      (query_list, self.attach_list) = self.read_mime_query_list(mimeinfo)
    else:
      istr = self.rfile.read(int(self.headers['content-length']))
      query_list = cgi.parse_qsl(istr, 1)
    self.input.update(dict(query_list))

  def do_POST(self):
    """The main POST shell.

    Keyword arguments:
    none

    """
    try:
      self.init_session()
      self.process_post_info()
      self.process_request()
    except:
      raise

  def do_GET(self):
    """The main GET shell.

    Keyword arguments:
    none

    """
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
    self.browser_output(200, self.mime_type, ''.join(self.output_buffer))

  pixel_data = open('images/pixel.gif').read()
  def pixel(self):
    self.browser_output(200, 'image/gif', self.pixel_data)
  up_data = open('images/up.gif').read()
  def up(self):
    self.browser_output(200, 'image/gif', self.up_data)
  down_data = open('images/down.gif').read()
  def down(self):
    self.browser_output(200, 'image/gif', self.down_data)
  favicon_data = open('images/favicon.ico').read()
  def favicon(self):
    self.browser_output(200, 'image/x-icon', self.favicon_data)

  def set_rating(self, item_uid, rating):
    from singleton import db
    c = db.cursor()
    c.execute('update fm_items set item_rating=%d where item_uid=%d'
              % (rating, item_uid))
    db.commit()
    c.close()

  def op_demote(self, item_uid):
    self.set_rating(item_uid, -1)
    
  def op_basic(self, item_uid):
    self.set_rating(item_uid, 0)
    
  def op_promote(self, item_uid):
    self.set_rating(item_uid, 1)

  def process_request(self):
    if not self.require_auth(param.auth_dict):
      return
    try:
      parts = self.path.split('?', 2)
      path = parts[0]
      if self.path in ['', '/']:
        self.browser_output(301, None, 'This document has moved.',
                            ['Location: /view'])
        return
      vars = []
      if len(parts) == 2:
        self.input.update(dict(cgi.parse_qsl(parts[1], 1)))

      if param.debug:
        logging.info((self.command, self.path, self.request_version, vars))

      if path == '/up.gif':
        self.up()
      if path == '/down.gif':
        self.down()

      if parts[0].count('favicon.ico') > 0:
        self.favicon()

      if path.startswith('/redirect/'):
        from singleton import db
        c = db.cursor()
        item_uid = int(path[10:])
        c.execute('select item_link from fm_items where item_uid=%d'
                  % item_uid)
        redirect_url = c.fetchone()[0]
        c.execute("""update fm_items set item_viewed=julianday("now")
        where item_uid=%d""" % item_uid)
        db.commit()
        c.close()
        self.browser_output(301, None, 'This document has moved.',
                            ['Location: ' + redirect_url])
        return

      if path.startswith('/feedback/'):
        op, item_uid = path.split('/')[2::2]
        item_uid = item_uid.split('.')[0]
        item_uid = int(item_uid)
        # for safety, these operations should be idempotent
        if op in ['promote', 'demote', 'basic']:
          getattr(self, 'op_' + op)(item_uid)
        self.pixel()

      # XXX use static compiled versions for speed
      page = 'pages/' + parts[0].split('/')[1] + '.tmpl'
      tmpl = TembozTemplate(file=page, searchList=[self.input])
      tmpl.respond(trans=self)
      self.flush()
    except:
      e = sys.exc_info()
      tmpl = Template(file='pages/error.tmpl')
      tmpl.e = e
      tmpl.respond(trans=self)
      self.flush()
      tmpl.e = None
      e = None
    return

def run():
  logging.getLogger().setLevel(logging.INFO)
  server = Server(('', param.port), Handler)
  server.serve_forever()
