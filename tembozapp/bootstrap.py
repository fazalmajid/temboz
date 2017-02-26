import sys, os, socket, string, getpass, passlib.hash

def do_bootstrap():
  dir = os.path.dirname(__file__ or os.getcwd())
  dir = os.getcwd() + os.sep + 'tempip' if dir == '.' else dir
  print """Welcome to the Temboz initial setup wizard!
  """
  ip, port = None, None
  while not ip or not port:
    bind = raw_input(
      """What IP address and TCP port should the server run on?
      Choose 127.0.0.1 to only allow connections from this machine (default)
      Choose 0.0.0.0 to allow connections from outside machines
Enter an IP address and port [127.0.0.1:9999]: """)
    bind = bind.strip()
    if not bind:
      bind = '127.0.0.1:9999'
    try:
      # IPv6 addresses can have colons too
      ip, port_s = bind.rsplit(':', 1)
    except ValueError:
      print >> sys.stderr,  'Invalid bind specification', bind,
      print >> sys.stderr,  '- it should be a of the form <IP>:<port>.'
      continue
    try:
      port = int(port_s)
    except ValueError:
      print >> sys.stderr,  'Invalid port number', port_s,
      print >> sys.stderr,  '- it should be a number between 1 and 65535.'
      continue
    if port < 1 or port > 65535:
      print >> sys.stderr,  'Invalid port number:', port,
      print >> sys.stderr, '- it should be a number between 1 and 65535.'
      port = None
    try:
      s = socket.socket()
      s.bind((ip, port))
      s.close()
    except socket.error as e:
      print >> sys.stderr,  'Cannot bind to', bind, '-', str(e)
      ip, port = None, None
      continue

  login = None
  while not login:
    login = raw_input(
      'Choose a username: ')
    login = login.strip()
    if not set(login).issubset(set(string.letters + string.digits + '_.')):
      print >> sys.stderr,  'Invalid username', login,
      print >> sys.stderr,  '- it should only have alphanumeric characters,',
      print >> sys.stderr,  'underscore or dot'
      login = None
      continue

  # implement NIST SP 800-63-3 password guidelines:
  #   https://pages.nist.gov/800-63-3/
  # XXX TODO not yet implementing bad password dictionary/bloom filter check
  passwd = None
  while not passwd:
    passwd = getpass.getpass('Enter password: ')
    if len(passwd) < 8:
      print >> sys.stderr, 'The password must have at least 8 characters'
      passwd = None
      continue
    if passwd != getpass.getpass('Confirm password: '):
      print >> sys.stderr,  'The passwords do not match'
      passwd = None
      continue
  hash = passlib.hash.argon2.using(
    rounds=64,
    memory_cost=65536,
    parallelism=1,
    digest_size=32).hash(passwd)

  os.system('sqlite3 rss.db < %s/ddl.sql' % dir)
  import dbop
  with dbop.db() as db:
    dbop.setting(db, 'login', login)
    dbop.setting(db, 'passwd', hash)
    dbop.setting(db, 'ip', ip)
    dbop.setting(db, 'port', str(port))
