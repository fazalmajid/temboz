import time, string, re, urllib
from Cheetah.Template import Template

class TembozTemplate(Template):
  def since(self, delta_t):
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
  def regurgitate_except(self, *exclude):
    """Regurgitate query string parameters as <input type="hidden"> fields
    to help maintain context in self-submitting forms"""
    opts = {}
    for d in self.searchList():
      if type(d) == dict:
        opts.update(d)
    return '\n'.join('<input type="hidden" name="%s" value="%s">'
                     % (name, urllib.quote_plus(value))
                     for (name, value) in opts.iteritems()
                     if set(name).issubset(self.valid_chars)
                     and name not in ('referer', 'headers')
                     and name not in exclude)
  def atom_content(self, content):
    # XXX should strip out tags that are inappropriate in a RSS reader
    # XXX such as <script>
    # see:
    #http://diveintomark.org/archives/2003/06/12/how_to_consume_rss_safely.html
    return ent_re.sub(ent_sub_xml, content)

# we do not support all HTML entities as only these are defined in XML
ent_dict_xml = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&apos;'
  }
ent_re = re.compile('([&<>"\'\x80-\xff])')
def ent_sub_xml(m):
  c = m.groups()[0]
  return ent_dict_xml.get(c, '&#%d;' % ord(c))
