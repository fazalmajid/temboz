#!/usr/bin/python
"""Ultra-liberal feed parser

Visit http://diveintomark.org/projects/feed_parser/ for the latest version

Handles RSS 0.9x, RSS 1.0, RSS 2.0, Atom feeds

Things it handles that choke other parsers:
- bastard combinations of RSS 0.9x and RSS 1.0
- illegal 8-bit XML characters
- naked and/or invalid HTML in description
- content:encoded, xhtml:body, fullitem
- guid
- elements in non-standard namespaces or non-default namespaces
- multiple content items per entry (Atom)
- multiple links per entry (Atom)

Other features:
- resolves relative URIs in some elements
  - uses xml:base to define base URI
  - uses URI of feed if no xml:base is given
  - to control which elements are resolved, set FeedParser.can_be_relative_uri
- resolves relative URIs within embedded markup
  - to control which elements are resolved, set FeedParser.can_contain_relative_uris
- sanitizes embedded markup in some elements
  - to allow/disallow HTML elements, set HTMLSanitizer.acceptable_elements
  - to allow/disallow HTML attributes, set HTMLSanitizer.acceptable_attributes
  - to control which feed elements are sanitized, set FeedParser.can_contain_dangerous_markup
  - to disable entirely (NOT RECOMMENDED), set FeedParser.can_contain_dangerous_markup = []
- tidies embedded markup
  - fixes malformed HTML
  - converts to XHTML
  - converts character entities to numeric entities
  - requires tidylib <http://utidylib.sourceforge.net/> or mxTidy <http://www.lemburg.com/files/python/mxTidy.html>

Requires Python 2.3 or later
"""

__version__ = "2.7"
__author__ = "Mark Pilgrim <http://diveintomark.org/>"
__copyright__ = "Copyright 2002-4, Mark Pilgrim"
__contributors__ = ["Jason Diamond <http://injektilo.org/>",
                    "John Beimler <http://john.beimler.org/>",
                    "Fazal Majid <http://www.majid.info/mylos/weblog/>"]
__license__ = "Python"
__history__ = """
1.0 - 9/27/2002 - MAP - fixed namespace processing on prefixed RSS 2.0 elements,
  added Simon Fell's test suite
1.1 - 9/29/2002 - MAP - fixed infinite loop on incomplete CDATA sections
2.0 - 10/19/2002
  JD - use inchannel to watch out for image and textinput elements which can
  also contain title, link, and description elements
  JD - check for isPermaLink="false" attribute on guid elements
  JD - replaced openAnything with open_resource supporting ETag and
  If-Modified-Since request headers
  JD - parse now accepts etag, modified, agent, and referrer optional
  arguments
  JD - modified parse to return a dictionary instead of a tuple so that any
  etag or modified information can be returned and cached by the caller
2.0.1 - 10/21/2002 - MAP - changed parse() so that if we don't get anything
  because of etag/modified, return the old etag/modified to the caller to
  indicate why nothing is being returned
2.0.2 - 10/21/2002 - JB - added the inchannel to the if statement, otherwise its
  useless.  Fixes the problem JD was addressing by adding it.
2.1 - 11/14/2002 - MAP - added gzip support
2.2 - 1/27/2003 - MAP - added attribute support, admin:generatorAgent.
  start_admingeneratoragent is an example of how to handle elements with
  only attributes, no content.
2.3 - 6/11/2003 - MAP - added USER_AGENT for default (if caller doesn't specify);
  also, make sure we send the User-Agent even if urllib2 isn't available.
  Match any variation of backend.userland.com/rss namespace.
2.3.1 - 6/12/2003 - MAP - if item has both link and guid, return both as-is.
2.4 - 7/9/2003 - MAP - added preliminary Pie/Atom/Echo support based on Sam Ruby's
  snapshot of July 1 <http://www.intertwingly.net/blog/1506.html>; changed
  project name
2.5 - 7/25/2003 - MAP - changed to Python license (all contributors agree);
  removed unnecessary urllib code -- urllib2 should always be available anyway;
  return actual url, status, and full HTTP headers (as result['url'],
  result['status'], and result['headers']) if parsing a remote feed over HTTP --
  this should pass all the HTTP tests at <http://diveintomark.org/tests/client/http/>;
  added the latest namespace-of-the-week for RSS 2.0
2.5.1 - 7/26/2003 - RMK - clear opener.addheaders so we only send our custom
  User-Agent (otherwise urllib2 sends two, which confuses some servers)
2.5.2 - 7/28/2003 - MAP - entity-decode inline xml properly; added support for
  inline <xhtml:body> and <xhtml:div> as used in some RSS 2.0 feeds
 2.5.3 - 8/6/2003 - TvdV - patch to track whether we're inside an image or
  textInput, and also to return the character encoding (if specified)
2.6 - 1/1/2004 - MAP - dc:author support (MarekK); fixed bug tracking
  nested divs within content (JohnD); fixed missing sys import (JohanS);
  fixed regular expression to capture XML character encoding (Andrei);
  added support for Atom 0.3-style links; fixed bug with textInput tracking;
  added support for cloud (MartijnP); added support for multiple
  category/dc:subject (MartijnP); normalize content model: "description" gets
  description (which can come from description, summary, or full content if no
  description), "content" gets dict of base/language/type/value (which can come
  from content:encoded, xhtml:body, content, or fullitem);
  fixed bug matching arbitrary Userland namespaces; added xml:base and xml:lang
  tracking; fixed bug tracking unknown tags; fixed bug tracking content when
  <content> element is not in default namespace (like Pocketsoap feed);
  resolve relative URLs in link, guid, docs, url, comments, wfw:comment,
  wfw:commentRSS; resolve relative URLs within embedded HTML markup in
  description, xhtml:body, content, content:encoded, title, subtitle,
  summary, info, tagline, and copyright; added support for pingback and
  trackback namespaces
2.7 - 1/5/2004 - MAP - really added support for trackback and pingback
  namespaces, as opposed to 2.6 when I said I did but didn't really;
  sanitize HTML markup within some elements; added mxTidy support (if
  installed) to tidy HTML markup within some elements; fixed indentation
  bug in parse_date (FazalM); use socket.setdefaulttimeout if available
  (FazalM); universal date parsing and normalization (FazalM): 'created', modified',
  'issued' are parsed into 9-tuple date format and stored in 'created_parsed',
  'modified_parsed', and 'issued_parsed'; 'date' is duplicated in 'modified'
  and vice-versa; 'date_parsed' is duplicated in 'modified_parsed' and vice-versa
"""

# if you are embedding feedparser in a larger application, you should change this to your application name and URL
USER_AGENT = "UltraLiberalFeedParser/%s +http://diveintomark.org/projects/feed_parser/" % __version__

# ---------- required modules (should come with any Python distribution) ----------
import cgi, re, sgmllib, string, StringIO, urllib2, sys, copy, urlparse, htmlentitydefs, time, rfc822

# ---------- optional modules (feedparser will work without these, but with reduced functionality) ----------

# gzip is included with most Python distributions, but may not be available if you compiled your own
try:
    import gzip
except:
    gzip = None
    
# timeoutsocket allows feedparser to time out rather than hang forever on ultra-slow servers.
# Python 2.3 now has this functionality available in the standard socket library, so under
# 2.3 you don't need to install anything.
import socket
if hasattr(socket, 'setdefaulttimeout'):
    socket.setdefaulttimeout(10)
else:
    try:
        import timeoutsocket # http://www.timo-tasi.org/python/timeoutsocket.py
        timeoutsocket.setDefaultSocketTimeout(10)
    except ImportError:
        pass

# mxtidy allows feedparser to tidy malformed embedded HTML markup in description, content, etc.
# this does not affect HTML sanitizing, which is self-contained in the HTMLSanitizer class
try:
    from mx.Tidy import Tidy as mxtidy # http://www.lemburg.com/files/python/mxTidy.html
except:
    mxtidy = None

# ---------- don't touch this ----------
sgmllib.tagfind = re.compile('[a-zA-Z][-_.:a-zA-Z0-9]*')

class FeedParser(sgmllib.SGMLParser):
    namespaces = {"http://backend.userland.com/rss": "",
                  "http://blogs.law.harvard.edu/tech/rss": "",
                  "http://purl.org/rss/1.0/": "",
                  "http://example.com/newformat#": "",
                  "http://example.com/necho": "",
                  "http://purl.org/echo/": "",
                  "uri/of/echo/namespace#": "",
                  "http://purl.org/pie/": "",
                  "http://purl.org/atom/ns#": "",
                  "http://purl.org/rss/1.0/modules/textinput/": "ti",
                  "http://purl.org/rss/1.0/modules/company/": "co",
                  "http://purl.org/rss/1.0/modules/syndication/": "sy",
                  "http://purl.org/dc/elements/1.1/": "dc",
                  "http://purl.org/dc/terms/": "dcterms",
                  "http://webns.net/mvcb/": "admin",
                  "http://wellformedweb.org/CommentAPI/": "wfw",
                  "http://madskills.com/public/xml/rss/module/trackback/": "trackback",
                  "http://madskills.com/public/xml/rss/module/pingback/": "pingback",
                  "http://www.w3.org/1999/xhtml": "xhtml"}

    can_be_relative_uri = ['link', 'id', 'guid', 'wfw_comment', 'wfw_commentRSS', 'docs', 'url', 'comments']
    can_contain_relative_uris = ['content', 'body', 'xhtml_body', 'content_encoded', 'fullitem', 'description', 'title', 'summary', 'subtitle', 'info', 'tagline', 'copyright']
    can_contain_dangerous_markup = ['content', 'body', 'xhtml_body', 'content_encoded', 'fullitem', 'description', 'title', 'summary', 'subtitle', 'info', 'tagline', 'copyright']
    explicitly_set_type = ['title', 'tagline', 'summary', 'info', 'copyright', 'content']
    html_types = ['text/html', 'application/xhtml+xml']
    
    def __init__(self, baseuri=None):
        sgmllib.SGMLParser.__init__(self)
        self.baseuri = baseuri or ''
        
    def reset(self):
        self.channel = {}
        self.items = []
        self.elementstack = []
        self.inchannel = 0
        self.initem = 0
        self.incontent = 0
        self.intextinput = 0
        self.inimage = 0
        self.contentparams = {}
        self.namespacemap = {}
        self.basestack = []
        self.langstack = []
        self.baseuri = ''
        self.lang = None
        sgmllib.SGMLParser.reset(self)

    def unknown_starttag(self, tag, attrs):
        # normalize attrs
        attrs = [(k.lower(), sgmllib.charref.sub(lambda m: chr(int(m.groups()[0])), v).strip()) for k, v in attrs]
        attrs = [(k, k in ('rel', 'type') and v.lower() or v) for k, v in attrs]
        
        # track inline content
        if self.incontent and self.contentparams.get('mode') == 'xml':
            return self.handle_data("<%s%s>" % (tag, "".join([' %s="%s"' % t for t in attrs])))

        # track xml:base and xml:lang
        attrsD = dict(attrs)
        baseuri = attrsD.get('xml:base')
        if baseuri:
            self.baseuri = baseuri
        lang = attrsD.get('xml:lang')
        if lang:
            self.lang = lang
        self.basestack.append(baseuri)
        self.langstack.append(lang)
        
        # track namespaces
        for prefix, value in attrs:
            if not prefix.startswith("xmlns:"): continue
            prefix = prefix[6:]
            if value.find('backend.userland.com/rss') <> -1:
                # match any backend.userland.com namespace
                value = 'http://backend.userland.com/rss'
            if self.namespaces.has_key(value):
                self.namespacemap[prefix] = self.namespaces[value]

        # match namespaces
        colonpos = tag.find(':')
        if colonpos <> -1:
            prefix = tag[:colonpos]
            suffix = tag[colonpos+1:]
            prefix = self.namespacemap.get(prefix, prefix)
            if prefix:
                prefix = prefix + '_'
        else:
            prefix = ''
            suffix = tag

        # call special handler (if defined) or default handler
        methodname = '_start_' + prefix + suffix
        try:
            method = getattr(self, methodname)
            return method(attrs)
        except AttributeError:
            return self.push(prefix + suffix, 1)

    def unknown_endtag(self, tag):
        # track inline content
        if self.incontent and self.contentparams.get('mode') == 'xml':
            self.handle_data("</%s>" % tag)

        # match namespaces
        colonpos = tag.find(':')
        if colonpos <> -1:
            prefix = tag[:colonpos]
            suffix = tag[colonpos+1:]
            prefix = self.namespacemap.get(prefix, prefix)
            if prefix:
                prefix = prefix + '_'
        else:
            prefix = ''
            suffix = tag

        # call special handler (if defined) or default handler
        methodname = '_end_' + prefix + suffix
        try:
            method = getattr(self, methodname)
            method()
        except AttributeError:
            self.pop(prefix + suffix)

        # track xml:base and xml:lang going out of scope
        if self.basestack:
            baseuri = self.basestack.pop()
            if baseuri:
                self.baseuri = baseuri
        if self.langstack:
            lang = self.langstack.pop()
            if lang:
                self.lang = lang

    def handle_charref(self, ref):
        # called for each character reference, e.g. for "&#160;", ref will be "160"
        # Reconstruct the original character reference.
        if not self.elementstack: return
        text = "&#%s;" % ref
        if self.incontent and self.contentparams.get('mode') == 'xml':
            text = cgi.escape(text)
        self.elementstack[-1][2].append(text)

    def handle_entityref(self, ref):
        # called for each entity reference, e.g. for "&copy;", ref will be "copy"
        # Reconstruct the original entity reference.
        if not self.elementstack: return
        text = "&%s;" % ref
        if self.incontent and self.contentparams.get('mode') == 'xml':
            text = cgi.escape(text)
        self.elementstack[-1][2].append(text)

    def handle_data(self, text):
        # called for each block of plain text, i.e. outside of any tag and
        # not containing any character or entity references
        if not self.elementstack: return
        if self.incontent and self.contentparams.get('mode') == 'xml':
            text = cgi.escape(text)
        self.elementstack[-1][2].append(text)

    def handle_comment(self, text):
        # called for each comment, e.g. <!-- insert message here -->
        pass

    def handle_pi(self, text):
        # called for each processing instruction, e.g. <?instruction>
        pass

    def handle_decl(self, text):
        # called for the DOCTYPE, if present, e.g.
        # <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        #     "http://www.w3.org/TR/html4/loose.dtd">
        pass

    _new_declname_match = re.compile(r'[a-zA-Z][-_.a-zA-Z0-9:]*\s*').match
    def _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        if i == n:
            return None, -1
        m = self._new_declname_match(rawdata, i)
        if m:
            s = m.group()
            name = s.strip()
            if (i + len(s)) == n:
                return None, -1  # end of buffer
            return string.lower(name), m.end()
        else:
            self.updatepos(declstartpos, i)
            self.error("expected name token")

    def parse_declaration(self, i):
        # override internal declaration handler to handle CDATA blocks
        if self.rawdata[i:i+9] == '<![CDATA[':
            k = self.rawdata.find(']]>', i)
            if k == -1: k = len(self.rawdata)
            self.handle_data(cgi.escape(self.rawdata[i+9:k]))
            return k+3
        return sgmllib.SGMLParser.parse_declaration(self, i)

    def resolveURI(self, uri):
        return urlparse.urljoin(self.baseuri or '', uri)
    
    def push(self, element, expectingText):
        self.elementstack.append([element, expectingText, []])

    def pop(self, element):
        if not self.elementstack: return
        if self.elementstack[-1][0] != element: return

        element, expectingText, pieces = self.elementstack.pop()
        if not expectingText: return
        
        output = "".join(pieces)
        output = output.strip()
        
        # resolve relative URIs
        if (element in self.can_be_relative_uri) and output:
            output = self.resolveURI(output)
        
        # decode entities within embedded markup
        if (element in self.explicitly_set_type and self.contentparams.get('type') in self.html_types) or \
           (element not in self.explicitly_set_type):
            output = output or ''
            output = output.replace('&lt;', '<')
            output = output.replace('&gt;', '>')
            output = output.replace('&quot;', '"')
            output = output.replace('&apos;', "'")
            output = output.replace('&amp;', '&')
        
        # resolve relative URIs within embedded markup
        if element in self.can_contain_relative_uris:
            output = resolveRelativeURIs(output, self.baseuri)
        
        # sanitize embedded markup
        if element in self.can_contain_dangerous_markup:
            output = sanitizeHTML(output)
            
        # store output in appropriate place(s)
        if self.incontent and self.initem:
            if not self.items[-1].has_key(element):
                self.items[-1][element] = []
            contentparams = copy.deepcopy(self.contentparams)
            contentparams['value'] = output
            self.items[-1][element].append(contentparams)
        elif self.initem:
            if element == 'category':
                domain = self.items[-1]['categories'][-1][0]
                self.items[-1]['categories'][-1] = (domain, output)
            elif element == 'link':
                if output:
                    self.items[-1]['links'][-1]['href'] = output
            self.items[-1][element] = output
        elif self.inchannel and (not self.intextinput) and (not self.inimage):
            if element == 'category':
                domain = self.channel['categories'][-1][0]
                self.channel['categories'][-1] = (domain, output)
            elif element == 'link':
                self.channel['links']['href'] = output
            self.channel[element] = output

        return output

    def _mapToStandardPrefix(self, name):
        colonpos = name.find(':')
        if colonpos <> -1:
            prefix = name[:colonpos]
            suffix = name[colonpos+1:]
            prefix = self.namespacemap.get(prefix, prefix)
            name = prefix + ':' + suffix
        return name
        
    def _getAttribute(self, attrs, name):
        return dict(attrs).get(self._mapToStandardPrefix(name))

    def _save(self, key, value):
        if value:
            if self.initem:
                self.items[-1].setdefault(key, value)
            elif self.channel:
                self.channel.setdefault(key, value)
        
    def _start_channel(self, attrs):
        self.inchannel = 1
    _start_feed = _start_channel

    def _end_channel(self):
        self.inchannel = 0
    _end_feed = _end_channel
    
    def _start_image(self, attrs):
        self.inimage = 1
            
    def _end_image(self):
        self.inimage = 0
                
    def _start_textinput(self, attrs):
        self.intextinput = 1
    _start_textInput = _start_textinput
    
    def _end_textinput(self):
        self.intextinput = 0
    _end_textInput = _end_textinput

    def _start_tagline(self, attrs):
        self.push('tagline', 1)

    def _end_tagline(self):
        value = self.pop('tagline')
        if self.inchannel:
            self.channel['description'] = value
            
    def _start_item(self, attrs):
        self.items.append({})
        self.push('item', 0)
        self.initem = 1
    _start_entry = _start_item

    def _end_item(self):
        self.pop('item')
        self.initem = 0
    _end_entry = _end_item

    def _start_dc_language(self, attrs):
        self.push('language', 1)
    _start_language = _start_dc_language

    def _end_dc_language(self):
        self.pop('language')
    _end_language = _end_dc_language

    def _start_dc_creator(self, attrs):
        self.push('creator', 1)
    _start_managingeditor = _start_dc_creator
    _start_webmaster = _start_dc_creator
    _start_name = _start_dc_creator

    def _end_dc_creator(self):
        self.pop('creator')
    _end_managingeditor = _end_dc_creator
    _end_webmaster = _end_dc_creator
    _end_name = _end_dc_creator

    def _start_dc_author(self, attrs):
        self.push('author', 1)
    _start_author = _start_dc_author

    def _end_dc_author(self):
        self.pop('author')
    _end_author = _end_dc_author
        
    def _start_dc_rights(self, attrs):
        self.push('rights', 1)
    _start_copyright = _start_dc_rights

    def _end_dc_rights(self):
        self.pop('rights')
    _end_copyright = _end_dc_rights

    def _start_dcterms_issued(self, attrs):
        self.push('issued', 1)
    _start_issued = _start_dcterms_issued

    def _end_dcterms_issued(self):
        value = self.pop('issued')
        self._save('issued_parsed', parse_date(value))
    _end_issued = _end_dcterms_issued

    def _start_dcterms_created(self, attrs):
        self.push('created', 1)
    _start_created = _start_dcterms_created

    def _end_dcterms_created(self):
        value = self.pop('created')
        self._save('created_parsed', parse_date(value))
    _end_created = _end_dcterms_created

    def _start_dcterms_modified(self, attrs):
        self.push('modified', 1)
    _start_modified = _start_dcterms_modified
    _start_dc_date = _start_dcterms_modified
    _start_pubdate = _start_dcterms_modified

    def _end_dcterms_modified(self):
        value = self.pop('modified')
        parsed_value = parse_date(value)
        self._save('date', value)
        self._save('date_parsed', parsed_value)
        self._save('modified_parsed', parsed_value)
    _end_modified = _end_dcterms_modified
    _end_dc_date = _end_dcterms_modified
    _end_pubdate = _end_dcterms_modified

    def _start_category(self, attrs):
        self.push('category', 1)
        domain = self._getAttribute(attrs, 'domain')
        cats = []
        if self.initem:
            cats = self.items[-1].setdefault('categories', [])
        elif self.inchannel:
            cats = self.channel.setdefault('categories', [])
        cats.append((domain, None))
    _start_dc_subject = _start_category
        
    def _end_category(self):
        self.pop('category')
    _end_dc_subject = _end_category
        
    def _start_link(self, attrs):
        attrsD = dict(attrs)
        attrsD.setdefault('rel', 'alternate')
        attrsD.setdefault('type', 'text/html')
        if attrsD.has_key('href'):
            attrsD['href'] = self.resolveURI(attrsD['href'])
        expectingText = self.inchannel or self.initem
        if self.initem:
            self.items[-1].setdefault('links', [])
            self.items[-1]['links'].append(attrsD)
        elif self.inchannel:
            self.channel['links'] = attrsD
        if attrsD.has_key('href'):
            expectingText = 0
            if attrsD.get('type', '') in self.html_types:
                if self.initem:
                    self.items[-1]['link'] = attrsD['href']
                elif self.inchannel:
                    self.channel['link'] = attrsD['href']
        else:
            self.push('link', expectingText)

    def _start_guid(self, attrs):
        self.guidislink = ('ispermalink', 'false') not in attrs
        self.push('guid', 1)

    def _end_guid(self):
        value = self.pop('guid')
        self._save('id', value)
        if self.guidislink:
            # guid acts as link, but only if "ispermalink" is not present or is "true",
            # and only if the item doesn't already have a link element
            self._save('link', value)

    def _start_id(self, attrs):
        self.push('id', 1)

    def _end_id(self):
        value = self.pop('id')
        self._save('guid', value)
            
    def _start_title(self, attrs):
        self.push('title', self.inchannel or self.initem)
    _start_dc_title = _start_title

    def _end_title(self):
        self.pop('title')
    _end_dc_title = _end_title

    def _start_description(self, attrs):
        self.push('description', self.inchannel or self.initem)

    def _end_description(self):
        value = self.pop('description')
        if self.initem:
            self.items[-1]['summary'] = value
        elif self.inchannel:
            self.channel['tagline'] = value
        
    def _start_admin_generatoragent(self, attrs):
        self.push('generator', 1)
        value = self._getAttribute(attrs, 'rdf:resource')
        if value:
            self.elementstack[-1][2].append(value)
        self.pop('generator')

    def _start_summary(self, attrs):
        self.push('summary', 1)

    def _end_summary(self):
        value = self.pop('summary')
        if self.items:
            self.items[-1]['description'] = value
        
    def _start_content(self, attrs):
        attrsD = dict(attrs)
        self.incontent += 1
        self.contentparams = {'mode': attrsD.get('mode', 'xml'),
                              'type': attrsD.get('type', 'text/plain'),
                              'language': attrsD.get('xml:lang', None),
                              'base': attrsD.get('xml:base', self.baseuri)}
        self.push('content', 1)

    def _start_body(self, attrs):
        attrsD = dict(attrs)
        self.incontent += 1
        self.contentparams = {'mode': 'xml',
                              'type': 'application/xhtml+xml',
                              'language': attrsD.get('xml:lang', None),
                              'base': attrsD.get('xml:base', self.baseuri)}
        self.push('content', 1)
    _start_xhtml_body = _start_body

    def _start_content_encoded(self, attrs):
        attrsD = dict(attrs)
        self.incontent += 1
        self.contentparams = {'mode': 'escaped',
                              'type': 'text/html',
                              'language': attrsD.get('xml:lang', None),
                              'base': attrsD.get('xml:base', self.baseuri)}
        self.push('content', 1)
    _start_fullitem = _start_content_encoded

    def _end_content(self):
        value = self.pop('content')
        if self.contentparams.get('type') in (['text/plain'] + self.html_types):
            self._save('description', value)
        self.incontent -= 1
        self.contentparams.clear()
    _end_body = _end_content
    _end_xhtml_body = _end_content
    _end_content_encoded = _end_content
    _end_fullitem = _end_content

class BaseHTMLProcessor(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        
    def reset(self):
        # extend (called by sgmllib.SGMLParser.__init__)
        self.pieces = []
        sgmllib.SGMLParser.reset(self)

    def normalize_attrs(self, attrs):
        # utility method to be called by descendants
        attrs = [(k.lower(), sgmllib.charref.sub(lambda m: chr(int(m.groups()[0])), v).strip()) for k, v in attrs]
        attrs = [(k, k in ('rel', 'type') and v.lower() or v) for k, v in attrs]
        return attrs

    def unknown_starttag(self, tag, attrs):
        # called for each start tag
        # attrs is a list of (attr, value) tuples
        # e.g. for <pre class="screen">, tag="pre", attrs=[("class", "screen")]
        strattrs = "".join([' %s="%s"' % (key, value) for key, value in attrs])
        self.pieces.append("<%(tag)s%(strattrs)s>" % locals())
        
    def unknown_endtag(self, tag):
        # called for each end tag, e.g. for </pre>, tag will be "pre"
        # Reconstruct the original end tag.
        self.pieces.append("</%(tag)s>" % locals())

    def handle_charref(self, ref):
        # called for each character reference, e.g. for "&#160;", ref will be "160"
        # Reconstruct the original character reference.
        self.pieces.append("&#%(ref)s;" % locals())
        
    def handle_entityref(self, ref):
        # called for each entity reference, e.g. for "&copy;", ref will be "copy"
        # Reconstruct the original entity reference.
        self.pieces.append("&%(ref)s" % locals())
        # standard HTML entities are closed with a semicolon; other entities are not
        if htmlentitydefs.entitydefs.has_key(ref):
            self.pieces.append(";")

    def handle_data(self, text):
        # called for each block of plain text, i.e. outside of any tag and
        # not containing any character or entity references
        # Store the original text verbatim.
        self.pieces.append(text)
        
    def handle_comment(self, text):
        # called for each HTML comment, e.g. <!-- insert Javascript code here -->
        # Reconstruct the original comment.
        self.pieces.append("<!--%(text)s-->" % locals())
        
    def handle_pi(self, text):
        # called for each processing instruction, e.g. <?instruction>
        # Reconstruct original processing instruction.
        self.pieces.append("<?%(text)s>" % locals())

    def handle_decl(self, text):
        # called for the DOCTYPE, if present, e.g.
        # <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        #     "http://www.w3.org/TR/html4/loose.dtd">
        # Reconstruct original DOCTYPE
        self.pieces.append("<!%(text)s>" % locals())
        
    def output(self):
        """Return processed HTML as a single string"""
        return "".join(self.pieces)

class RelativeURIResolver(BaseHTMLProcessor):
    relative_uris = [('a', 'href'),
                     ('applet', 'codebase'),
                     ('area', 'href'),
                     ('blockquote', 'cite'),
                     ('body', 'background'),
                     ('del', 'cite'),
                     ('form', 'action'),
                     ('frame', 'longdesc'),
                     ('frame', 'src'),
                     ('iframe', 'longdesc'),
                     ('iframe', 'src'),
                     ('head', 'profile'),
                     ('img', 'longdesc'),
                     ('img', 'src'),
                     ('img', 'usemap'),
                     ('input', 'src'),
                     ('input', 'usemap'),
                     ('ins', 'cite'),
                     ('link', 'href'),
                     ('object', 'classid'),
                     ('object', 'codebase'),
                     ('object', 'data'),
                     ('object', 'usemap'),
                     ('q', 'cite'),
                     ('script', 'src')]

    def __init__(self, baseuri):
        BaseHTMLProcessor.__init__(self)
        self.baseuri = baseuri

    def resolveURI(self, uri):
        return urlparse.urljoin(self.baseuri, uri)
    
    def unknown_starttag(self, tag, attrs):
        attrs = self.normalize_attrs(attrs)
        attrs = [(key, ((tag, key) in self.relative_uris) and self.resolveURI(value) or value) for key, value in attrs]
        BaseHTMLProcessor.unknown_starttag(self, tag, attrs)
        
def resolveRelativeURIs(htmlSource, baseURI):
    p = RelativeURIResolver(baseURI)
    p.feed(htmlSource)
    data = p.output()
    return data

class HTMLSanitizer(BaseHTMLProcessor):
    acceptable_elements = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'big',
      'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col',
      'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset',
      'font', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input',
      'ins', 'kbd', 'label', 'legend', 'li', 'map', 'menu', 'ol', 'optgroup',
      'option', 'p', 'pre', 'q', 's', 'samp', 'select', 'small', 'span', 'strike',
      'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th',
      'thead', 'tr', 'tt', 'u', 'ul', 'var']
    
    acceptable_attributes = ['abbr', 'accept', 'accept-charset', 'accesskey',
      'action', 'align', 'alt', 'axis', 'border', 'cellpadding', 'cellspacing',
      'char', 'charoff', 'charset', 'checked', 'cite', 'class', 'clear', 'cols',
      'colspan', 'color', 'compact', 'coords', 'datetime', 'dir', 'disabled',
      'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace',
      'id', 'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method',
      'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly',
      'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape', 'size',
      'span', 'src', 'start', 'summary', 'tabindex', 'target', 'title', 'type',
      'usemap', 'valign', 'value', 'vspace', 'width']
    
    def unknown_starttag(self, tag, attrs):
        if not tag in self.acceptable_elements: return
        attrs = self.normalize_attrs(attrs)
        attrs = [(key, value) for key, value in attrs if key in self.acceptable_attributes]
        BaseHTMLProcessor.unknown_starttag(self, tag, attrs)
        
    def unknown_endtag(self, tag):
        if not tag in self.acceptable_elements: return
        BaseHTMLProcessor.unknown_endtag(self, tag)

    def handle_pi(self, text):
        pass

    def handle_decl(self, text):
        pass

def sanitizeHTML(htmlSource):
    p = HTMLSanitizer()
    p.feed(htmlSource)
    data = p.output()
    if mxtidy:
        nerrors, nwarnings, data, errordata = mxtidy.tidy(data, output_xhtml=1, numeric_entities=1, wrap=0)
        if data.count('<body'):
            data = data.split('<body', 1)[1]
            if data.count('>'):
                data = data.split('>', 1)[1]
        if data.count('</body'):
            data = data.split('</body', 1)[0]
        data = data.strip()
    return data

class FeedURLHandler(urllib2.HTTPRedirectHandler, urllib2.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        if ((code / 100) == 3) and (code != 304):
            return self.http_error_302(req, fp, code, msg, headers)
        from urllib import addinfourl
        infourl = addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        return infourl
#        raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)

    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        infourl.status = code
        return infourl

    def http_error_301(self, req, fp, code, msg, headers):
        infourl = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        infourl.status = code
        return infourl

    http_error_300 = http_error_302
    http_error_307 = http_error_302
        
def open_resource(source, etag=None, modified=None, agent=None, referrer=None):
    """
    URI, filename, or string --> stream

    This function lets you define parsers that take any input source
    (URL, pathname to local or network file, or actual data as a string)
    and deal with it in a uniform manner.  Returned object is guaranteed
    to have all the basic stdio read methods (read, readline, readlines).
    Just .close() the object when you're done with it.

    If the etag argument is supplied, it will be used as the value of an
    If-None-Match request header.

    If the modified argument is supplied, it must be a tuple of 9 integers
    as returned by gmtime() in the standard Python time module. This MUST
    be in GMT (Greenwich Mean Time). The formatted date/time will be used
    as the value of an If-Modified-Since request header.

    If the agent argument is supplied, it will be used as the value of a
    User-Agent request header.

    If the referrer argument is supplied, it will be used as the value of a
    Referer[sic] request header.
    """

    if hasattr(source, "read"):
        return source

    if source == "-":
        return sys.stdin

    if not agent:
        agent = USER_AGENT
        
    # try to open with urllib2 (to use optional headers)
    request = urllib2.Request(source)
    if etag:
        request.add_header("If-None-Match", etag)
    if modified:
        request.add_header("If-Modified-Since", format_http_date(modified))
    request.add_header("User-Agent", agent)
    if referrer:
        request.add_header("Referer", referrer)
        if gzip:
            request.add_header("Accept-encoding", "gzip")
    opener = urllib2.build_opener(FeedURLHandler())
    opener.addheaders = [] # RMK - must clear so we only send our custom User-Agent
    try:
        return opener.open(request)
    except:
        # source is not a valid URL, but it might be a valid filename
        pass
    
    # try to open with native open function (if source is a filename)
    try:
        return open(source)
    except:
        pass

    # treat source as string
    return StringIO.StringIO(str(source))

def get_etag(resource):
    """
    Get the ETag associated with a response returned from a call to 
    open_resource().

    If the resource was not returned from an HTTP server or the server did
    not specify an ETag for the resource, this will return None.
    """

    if hasattr(resource, "info"):
        return resource.info().getheader("ETag")
    return None

def get_modified(resource):
    """
    Get the Last-Modified timestamp for a response returned from a call to
    open_resource().

    If the resource was not returned from an HTTP server or the server did
    not specify a Last-Modified timestamp, this function will return None.
    Otherwise, it returns a tuple of 9 integers as returned by gmtime() in
    the standard Python time module().
    """

    if hasattr(resource, "info"):
        last_modified = resource.info().getheader("Last-Modified")
        if last_modified:
            return parse_date(last_modified)
    return None

short_weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
long_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def format_http_date(date):
    """
    Formats a tuple of 9 integers into an RFC 1123-compliant timestamp as
    required in RFC 2616. We don't use time.strftime() since the %a and %b
    directives can be affected by the current locale (HTTP dates have to be
    in English). The date MUST be in GMT (Greenwich Mean Time).
    """

    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (short_weekdays[date[6]], date[2], months[date[1] - 1], date[0], date[3], date[4], date[5])

# if possible, use the PyXML module xml.utils.iso8601 to parse dates
try:
    from xml.utils.iso8601 import parse as iso8601_parse
except ImportError:
    iso8601_parse = None

# the ISO 8601 standard is very convoluted and irregular - a full ISO 8601
# parser is beyond the scope of feedparser and would be a worthwhile addition
# to the Python library
# A single regular expression cannot parse ISO 8601 date formats into groups
# as the standard is highly irregular (for instance is 030104 2003-01-04 or
# 0301-04-01), so we use templates instead
# Please note the order in templates is significant because we need  a
# greedy match
iso8601_tmpl = ['YYYY-?MM-?DD', 'YYYY-MM', 'YYYY-?OOO',
                'YY-?MM-?DD', 'YY-?OOO', 'YYYY', 
                '-YY-?MM', '-OOO', '-YY',
                '--MM-?DD', '--MM',
                '---DD',
                'CC', '']
iso8601_re = [
    tmpl.replace(
    'YYYY', r'(?P<year>\d{4})').replace(
    'YY', r'(?P<year>\d\d)').replace(
    'MM', r'(?P<month>[01]\d)').replace(
    'DD', r'(?P<day>[0123]\d)').replace(
    'OOO', r'(?P<ordinal>[0123]\d\d)').replace(
    'CC', r'(?P<century>\d\d$)')
    + r'(T?(?P<hour>\d{2}):(?P<minute>\d{2})'
    + r'(:(?P<second>\d{2}))?'
    + r'(?P<tz>[+-](?P<tzhour>\d{2})(:(?P<tzmin>\d{2}))?|Z)?)?'
    for tmpl in iso8601_tmpl]

iso8601_matches = [re.compile(regex).match for regex in iso8601_re]

def parse_date(date):
    """
    Parses a variety of date formats into a tuple of 9 integers as
    returned by time.gmtime(). This should not use time.strptime() since
    that function is not available on all platforms and could also be
    affected by the current locale.
    """

    date = str(date)

    try:
        # if at all possible, use the standard library's rfc822 module's
        # (RFC2822, actually, which also encompasses RFC1123)
        # parsedate function instead of rolling our own
        # rfc822.parsedate is quite robust, and handles asctime-style dates
        # as well
        tm = rfc822.parsedate_tz(date)
        if tm:
            return time.gmtime(rfc822.mktime_tz(tm))
        # not a RFC2822 date, try ISO 8601 format instead
        try:
            if iso8601_parse:
                tm = iso8601_parse(date)
        except ValueError:
            tm = None
        if tm:
            return time.gmtime(tm)
        # unfortunately, xml.utils.iso8601 does not recognize many valid
        # ISO8601 formats like 20040105, so we try our home-made
        # regular expressions instead
        for iso8601_match in iso8601_matches:
            m = iso8601_match(date)
            if m:
                break
        if not m:
            return None
        # catch truly malformed strings
        if m.span() == (0, 0):
            return None
        params = m.groupdict()
        ordinal = params.get("ordinal", 0)
        if ordinal:
            ordinal = int(ordinal)
        else:
            ordinal = 0
        year = params.get("year", "--")
        if not year or year == "--":
            year = time.gmtime()[0]
        elif len(year) == 2:
            # ISO 8601 assumes current century, i.e. 93 -> 2093, NOT 1993
            year = 100 * (time.gmtime()[0] // 100) + int(year)
        else:
            year = int(year)
        month = params.get("month", "-")
        if not month or month == "-":
            # ordinals are NOT normalized by mktime, we simulate them
            # by setting month=1, day=ordinal
            if ordinal:
                month = 1
            else:
                month = time.gmtime()[1]
        month = int(month)
        day = params.get("day", 0)
        if not day:
            # see above
            if ordinal:
                day = ordinal
            elif params.get("century", 0) or \
                     params.get("year", 0) or params.get("month", 0):
                day = 1
            else:
                day = time.gmtime()[2]
        else:
            day = int(day)
        # special case of the century - is the first year of the 21st century
        # 2000 or 2001 ? The debate goes on...
        if "century" in params:
            year = (int(params["century"]) - 1) * 100 + 1
        # in ISO 8601 most fields are optional
        for field in ["hour", "minute", "second", "tzhour", "tzmin"]:
            if not params.get(field, None):
                params[field] = 0
        hour = int(params.get("hour", 0))
        minute = int(params.get("minute", 0))
        second = int(params.get("second", 0))
        # weekday is normalized by mktime(), we can ignore it
        weekday = 0
        # daylight savings is complex, but not needed for feedparser's purposes
        # as time zones, if specified, include mention of whether it is active
        # (e.g. PST vs. PDT, CET). Using -1 is implementation-dependent and
        # and most implementations have DST bugs
        daylight_savings_flag = 0
        tm = [year, month, day, hour, minute, second, weekday,
              ordinal, daylight_savings_flag]
        # ISO 8601 time zone adjustments
        tz = params.get("tz")
        if tz and tz != "Z":
            if tz[0] == "-":
                tm[3] += int(params.get("tzhour", 0))
                tm[4] += int(params.get("tzmin", 0))
            elif tz[0] == "+":
                tm[3] -= int(params.get("tzhour", 0))
                tm[4] -= int(params.get("tzmin", 0))
            else:
                return None
        # Python's time.mktime() is a wrapper around the ANSI C mktime(3c)
        # which is guaranteed to normalize d/m/y/h/m/s
        # many implementations have bugs, however
        return time.localtime(time.mktime(tm))
    except:
        return None

def parse(uri, etag=None, modified=None, agent=None, referrer=None):
    result = {}
    f = open_resource(uri, etag=etag, modified=modified, agent=agent, referrer=referrer)
    data = f.read()
    if hasattr(f, "headers"):
        if gzip and f.headers.get('content-encoding', '') == 'gzip':
            try:
                data = gzip.GzipFile(fileobj=StringIO.StringIO(data)).read()
            except:
                # some feeds claim to be gzipped but they're not, so we get garbage
                data = ''
    newEtag = get_etag(f)
    if newEtag: result["etag"] = newEtag
    elif etag: result["etag"] = etag
    newModified = get_modified(f)
    if newModified: result["modified"] = newModified
    elif modified: result["modified"] = modified
    if hasattr(f, "url"):
        result["url"] = f.url
    if hasattr(f, "headers"):
        result["headers"] = f.headers.dict
    if hasattr(f, "status"):
        result["status"] = f.status
    elif hasattr(f, "url"):
        result["status"] = 200
    # get the xml encoding
#    xmlheaderRe = re.compile('<\?.*encoding="(.*)".*\?>') # TvdV's version
#    xmlheaderRe = re.compile('xml\s.*\sencoding=(".*"|\'.*\').*') # Blake's version
    xmlheaderRe = re.compile('<\?.*encoding=[\'"](.*?)[\'"].*\?>') # Andrei's version
    match = xmlheaderRe.match(data)
    if match:
        result['encoding'] = match.groups()[0].lower()
    f.close()
    baseuri = result.get('headers', {}).get('content-location', result.get('url'))
    r = FeedParser(baseuri)
    r.feed(data)
    result['channel'] = r.channel
    result['items'] = r.items
    return result

TEST_SUITE = ('http://www.pocketsoap.com/rssTests/rss1.0withModules.xml',
              'http://www.pocketsoap.com/rssTests/rss1.0withModulesNoDefNS.xml',
              'http://www.pocketsoap.com/rssTests/rss1.0withModulesNoDefNSLocalNameClash.xml',
              'http://www.pocketsoap.com/rssTests/rss2.0noNSwithModules.xml',
              'http://www.pocketsoap.com/rssTests/rss2.0noNSwithModulesLocalNameClash.xml',
              'http://www.pocketsoap.com/rssTests/rss2.0NSwithModules.xml',
              'http://www.pocketsoap.com/rssTests/rss2.0NSwithModulesNoDefNS.xml',
              'http://www.pocketsoap.com/rssTests/rss2.0NSwithModulesNoDefNSLocalNameClash.xml')

last_day_year = time.localtime(time.mktime(
    (time.gmtime()[0], 12, 31, 0, 0, 0, 0, 0, 0)))
last_day_january = time.localtime(time.mktime(
    (time.gmtime()[0], 1, 31, 0, 0, 0, 0, 0, 0)))
first_day_month = time.localtime(time.mktime(
    (time.gmtime()[0], time.gmtime()[1], 1, 0, 0, 0, 0, 0, 0)))
first_day_december = time.localtime(time.mktime(
    (time.gmtime()[0], 12, 1, 0, 0, 0, 0, 0, 0)))
DATETIME_SUITE = (
    ('asctime', 'Sun Jan  4 16:29:06 PST 2004',
     (2004, 1, 5, 0, 29, 6, 0, 5, 0)),
    ('RFC-2822', 'Sat, 03 Jan 2004 07:21:52 GMT',
     (2004, 1, 3, 7, 21, 52, 5, 3, 0)),
    # http://www.w3.org/TR/NOTE-datetime
    ('W3C-datetime (Tokyo)', '2003-12-31T18:14:55+08:00',
     (2003, 12, 31, 10, 14, 55, 2, 365, 0)),
    ('W3C-datetime (San Francisco)', '2003-12-31T10:14:55-08:00',
     (2003, 12, 31, 18, 14, 55, 2, 365, 0)),
    ('W3C-datetime (zulu)', '2003-12-31T10:14:55Z',
     (2003, 12, 31, 10, 14, 55, 2, 365, 0)),
    # Complete ISO 8601 test cases for the sake of completeness
    # See:
    # http://www.cl.cam.ac.uk/~mgk25/iso-time.html
    # http://www.mcs.vuw.ac.nz/technical/software/SGML/doc/iso8601/ISO8601.html
    ('ISO8601 date only', '2003-12-31',
     (2003, 12, 31, 0, 0, 0, 2, 365, 0)),
    ('ISO8601 date only (variant)', '20031231',
     (2003, 12, 31, 0, 0, 0, 2, 365, 0)),
    ('ISO8601 year/month only', '2003-12',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 year only', '2003',
     (2003, 1, 1, 0, 0, 0, 2, 1, 0)),
    ('ISO8601 century only', '21',
     (2001, 1, 1, 0, 0, 0, 0, 1, 0)),
    ('ISO8601 century omitted', '03-12-31',
     (2003, 12, 31, 0, 0, 0, 2, 365, 0)),
    ('ISO8601 century omitted (variant)', '031231',
     (2003, 12, 31, 0, 0, 0, 2, 365, 0)),
    ('ISO8601 year/month only (century omitted)', '-03-12',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 year/month only (century omitted variant)', '-0312',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 year only (century omitted)', '-03',
     (2003, 1, 1, 0, 0, 0, 2, 1, 0)),
    ('ISO8601 day/month only (year omitted)', '--12-31', last_day_year),
    ('ISO8601 day/month only (year omitted variant)', '--1231', last_day_year),
    ('ISO8601 month only', '--12', first_day_december),
    ('ISO8601 day only', '---01', first_day_month),
    ('ISO8601 year/ordinal', '2003-335',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 year/ordinal (variant)', '2003335',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 year/ordinal (century omitted)', '03-335',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 year/ordinal (century omitted variant)', '03335',
     (2003, 12, 1, 0, 0, 0, 0, 335, 0)),
    ('ISO8601 ordinal only', '-%03d' % last_day_year[-2], last_day_year),
    ('ISO8601 ordinal only', '-031', last_day_january),
    # XXX missing ISO 8601 week/day formats
    # time formats
    ('ISO8601 time only', '17:41:00',
     time.gmtime()[0:3] + (17, 41 ,00) + time.gmtime()[-3:]),
    ('ISO8601 time only (zulu)', '17:41:00Z',
     time.gmtime()[0:3] + (17, 41 ,00) + time.gmtime()[-3:]),
    ('ISO8601 time only (Tokyo)', '18:14:55+08:00',
     time.gmtime()[0:3] + (10, 14, 55) + time.gmtime()[-3:]),
    ('ISO8601 time only (Tokyo)', '18:14:55+08',
     time.gmtime()[0:3] + (10, 14, 55) + time.gmtime()[-3:]),
    # rollover, leap years, and so on
    ('Rollover', '2004-02-28T18:14:55-08:00',
     (2004, 2, 29, 2, 14, 55, 6, 60, 0)),
    ('Rollover', '2003-02-28T18:14:55-08:00',
     (2003, 3, 1, 2, 14, 55, 5, 60, 0)),
    ('Rollover (Y2K)', '2000-02-28T18:14:55-08:00',
     (2000, 2, 29, 2, 14, 55, 1, 60, 0)),
    # this will overflow due to 32-bit time_t overflow
    # years multiple of 100 but not of 400 are not leap years, e.g. 1900, 2100
    ('Rollover (2100) (IGNORE)', '2100-02-28T18:14:55-08:00',
     (2100, 3, 1, 2, 14, 55, 0, 60, 0)),
    # miscellaneous non-conforming formats, seen in the wild
    ('Bogus (from http://mindview.net/WebLog/RSS.xml)', '1-2-04', None),
    ('US-style date only', '04-01-05',
     (2004, 1, 5, 0, 0, 0, 0, 5, 0)))
    

if __name__ == '__main__':
    if sys.argv[1:] == ['date']:
        for test, date, gmtime in DATETIME_SUITE:
            result = parse_date(date)
            if result != gmtime:
                print '### failed test for', test, '("%s")' % date
                print 'got',  result, 'expected', gmtime
        sys.exit(0)
    if sys.argv[1:]:
        urls = sys.argv[1:]
    else:
        urls = TEST_SUITE
    from pprint import pprint
    for url in urls:
        print url
        print
        result = parse(url)
        pprint(result)
        print

"""
TODO
- image
- author
- contributor
- comments
- base64 content
"""
