# -*- coding: iso-8859-1 -*-
from __future__ import print_function
import sys, time, re, codecs, string, traceback, socket, hashlib
import unicodedata, requests, feedparser
from . import param, transform, util, porter2
import bleach

try:
  import html.entities as htmlentitydefs
except ImportError:
  import htmlentitydefs

# XXX TODO
#
# XXX normalize feed['title'] to quote &amp; &quot;
#
# XXX Many of these heuristics have probably been addressed by newer versions
# XXX of feedparser.py

#date_fmt = '%a, %d %b %Y %H:%M:%S %Z'
date_fmt = '%Y-%m-%d %H:%M:%S'

try:
  try:
    import ctranslitcodec as translitcodec
  except ImportError:
    import translitcodec
  def strip_diacritics(s):
    return translitcodec.short_encode(s)[0]
except ImportError:
  # strip diacritics. Unicode normalization form D (NFD) maps letters with
  # diacritics into the base letter followed by a combining diacritic, all
  # we need to do is get rid of the combining diacritics
  # this probably does not work with exotic characters like
  # U+FDF2 (Arabic ligature Allah)
  def stripc(c):
    return unicodedata.normalize('NFD', c)[0]
  def strip_diacritics(s):
    return ''.join(map(stripc, s))

# XXX need a good way to support languages other than English and French
stop_words = ['i', 't', 'am', 'no', 'do', 's', 'my', 'don', 'm', 'on',
              'get', 'in', 'you', 'me', 'd', 've']
# list originally from: http://bll.epnet.com/help/ehost/Stop_Words.htm
stop_words += ['a', 'the', 'of', 'and', 'that', 'for', 'by', 'as', 'be',
'or', 'this', 'then', 'we', 'which', 'with', 'at', 'from', 'under',
'such', 'there', 'other', 'if', 'is', 'it', 'can', 'now', 'an', 'to',
'but', 'upon', 'where', 'these', 'when', 'whether', 'also', 'than',
'after', 'within', 'before', 'because', 'without', 'however',
'therefore', 'between', 'those', 'since', 'into', 'out', 'some', 'about',
'accordingly', 'again', 'against', 'all', 'almost', 'already',
'although', 'always', 'among', 'any', 'anyone', 'apparently', 'are',
'arise', 'aside', 'away', 'became', 'become', 'becomes', 'been', 'being',
'both', 'briefly', 'came', 'cannot', 'certain', 'certainly', 'could',
'etc', 'does', 'done', 'during', 'each', 'either', 'else', 'ever',
'every', 'further', 'gave', 'gets', 'give', 'given', 'got', 'had',
'hardly', 'has', 'have', 'having', 'here', 'how', 'itself', 'just',
'keep', 'kept', 'largely', 'like', 'made', 'mainly', 'make', 'many',
'might', 'more', 'most', 'mostly', 'much', 'must', 'nearly',
'necessarily', 'neither', 'next', 'none', 'nor', 'normally', 'not',
'noted', 'often', 'only', 'our', 'put', 'owing', 'particularly',
'perhaps', 'please', 'potentially', 'predominantly', 'present',
'previously', 'primarily', 'probably', 'prompt', 'promptly', 'quickly',
'quite', 'rather', 'readily', 'really', 'recently', 'regarding',
'regardless', 'relatively', 'respectively', 'resulted', 'resulting',
'results', 'said', 'same', 'seem', 'seen', 'several', 'shall', 'should',
'show', 'showed', 'shown', 'shows', 'significantly', 'similar',
'similarly', 'slightly', 'so', 'sometime', 'somewhat', 'soon',
'specifically', 'strongly', 'substantially', 'successfully',
'sufficiently', 'their', 'theirs', 'them', 'they', 'though', 'through',
'throughout', 'too', 'toward', 'unless', 'until', 'use', 'used', 'using',
'usually', 'various', 'very', 'was', 'were', 'what', 'while', 'who',
'whose', 'why', 'widely', 'will', 'would', 'yet']
# French stop words
# list originally from: http://www.up.univ-mrs.fr/veronis/data/antidico.txt
# XXX it's not good practice to mix languages like this, we should use
# XXX feed language metadata and track what language a content is written in
# XXX but that would require significant data model changes
dec = (lambda s: unicode(s, 'iso8859-15')) if sys.version < '3' else str
stop_words += [strip_diacritics(dec(s)) for s in [
  "a", "A", "à", "afin", "ah", "ai", "aie", "aient", "aies", "ailleurs",
  "ainsi", "ait", "alentour", "alias", "allais", "allaient",
  "allait", "allons", "allez", "alors", "Ap.", "Apr.", "après",
  "après-demain", "arrière", "as", "assez", "attendu", "au", "aucun",
  "aucune", "au-dedans", "au-dehors", "au-delà", "au-dessous",
  "au-dessus", "au-devant", "audit", "aujourd'", "aujourd'hui",
  "auparavant", "auprès", "auquel", "aura", "aurai", "auraient",
  "aurais", "aurait", "auras", "aurez", "auriez", "aurions",
  "aurons", "auront", "aussi", "aussitôt", "autant", "autour", "autre",
  "autrefois", "autres", "autrui", "aux", "auxdites", "auxdits",
  "auxquelles", "auxquels", "avaient", "avais", "avait", "avant",
  "avant-hier", "avec", "avez", "aviez", "avions", "avoir", "avons",
  "ayant", "ayez", "ayons", "B", "bah", "banco", "bé", "beaucoup", "ben",
  "bien", "bientôt", "bis", "bon", "ç'", "c.-à-d.", "Ca", "ça", "çà",
  "cahin-caha", "car", "ce", "-ce", "céans", "ceci", "cela", "celle",
  "celle-ci", "celle-là", "celles", "celles-ci", "celles-là", "celui",
  "celui-ci", "celui-là", "cent", "cents", "cependant", "certain",
  "certaine", "certaines", "certains", "certes", "ces", "c'est-à-dire",
  "cet", "cette", "ceux", "ceux-ci", "ceux-là", "cf.", "cg", "cgr",
  "chacun", "chacune", "chaque", "cher", "chez", "ci", "-ci", "ci-après",
  "ci-dessous", "ci-dessus", "cinq", "cinquante", "cinquante-cinq",
  "cinquante-deux", "cinquante-et-un", "cinquante-huit",
  "cinquante-neuf", "cinquante-quatre", "cinquante-sept",
  "cinquante-six", "cinquante-trois", "cl", "cm", "cm²", "combien",
  "comme", "comment", "contrario", "contre", "crescendo", "D", "d'",
  "d'abord", "d'accord", "d'affilée", "d'ailleurs", "dans", "d'après",
  "d'arrache-pied", "davantage", "de", "debout", "dedans", "dehors",
  "déjà", "delà", "demain", "d'emblée", "depuis", "derechef",
  "derrière", "des", "dès", "desdites", "desdits", "désormais",
  "desquelles", "desquels", "dessous", "dessus", "deux", "devant",
  "devers", "dg", "die", "différentes", "différents", "dire", "dis",
  "disent", "dit", "dito", "divers", "diverses", "dix", "dix-huit",
  "dix-neuf", "dix-sept", "dl", "dm", "donc", "dont", "dorénavant",
  "douze", "du", "dû", "dudit", "duquel", "durant", "E", "eh", "elle",
  "-elle", "elles", "-elles", "en", "'en", "-en", "encore", "enfin",
  "ensemble", "ensuite", "entre", "entre-temps", "envers", "environ",
  "es", "ès", "est", "et", "et/ou", "étaient", "étais", "était", "étant",
  "etc", "été", "êtes", "étiez", "étions", "être", "eu", "eue", "eues",
  "euh", "eûmes", "eurent", "eus", "eusse", "eussent", "eusses",
  "eussiez", "eussions", "eut", "eût", "eûtes", "eux", "exprès",
  "extenso", "extremis", "F", "facto", "fallait", "faire", "fais",
  "faisais", "faisait", "faisaient", "faisons", "fait", "faites",
  "faudrait", "faut", "fi", "flac", "fors", "fort", "forte", "fortiori",
  "frais", "fûmes", "fur", "furent", "fus", "fusse", "fussent", "fusses",
  "fussiez", "fussions", "fut", "fût", "fûtes", "G", "GHz", "gr",
  "grosso", "guère", "H", "ha", "han", "haut", "hé", "hein", "hem",
  "heu", "hg", "hier", "hl", "hm", "hm³", "holà", "hop", "hormis", "hors",
  "hui", "huit", "hum", "I", "ibidem", "ici", "ici-bas", "idem", "il",
  "-il", "illico", "ils", "-ils", "ipso", "item", "J", "j'", "jadis",
  "jamais", "je", "-je", "jusqu'", "jusqu'à", "jusqu'au", "jusqu'aux",
  "jusque", "juste", "K", "kg", "km", "km²", "L", "l'", "la", "-la", "là",
  "-là", "là-bas", "là-dedans", "là-dehors", "là-derrière",
  "là-dessous", "là-dessus", "là-devant", "là-haut", "laquelle",
  "l'autre", "le", "-le", "lequel", "les", "-les", "lès", "lesquelles",
  "lesquels", "leur", "-leur", "leurs", "lez", "loin", "l'on",
  "longtemps", "lors", "lorsqu'", "lorsque", "lui", "-lui", "l'un",
  "l'une", "M", "m'", "m²", "m³", "ma", "maint", "mainte", "maintenant",
  "maintes", "maints", "mais", "mal", "malgré", "me", "même", "mêmes",
  "mes", "mg", "mgr", "MHz", "mieux", "mil", "mille", "milliards",
  "millions", "minima", "ml", "mm", "mm²", "modo", "moi", "-moi", "moins",
  "mon", "moult", "moyennant", "mt", "N", "n'", "naguère", "ne",
  "néanmoins", "neuf", "ni", "nº", "non", "nonante", "nonobstant", "nos",
  "notre", "nous", "-nous", "nul", "nulle", "O", "ô", "octante", "oh",
  "on", "-on", "ont", "onze", "or", "ou", "où", "ouais", "oui", "outre",
  "P", "par", "parbleu", "parce", "par-ci", "par-delà", "par-derrière",
  "par-dessous", "par-dessus", "par-devant", "parfois", "par-là",
  "parmi", "partout", "pas", "passé", "passim", "pendant", "personne",
  "petto", "peu", "peut", "peuvent", "peux", "peut-être", "pis", "plus",
  "plusieurs", "plutôt", "point", "posteriori", "pour", "pourquoi",
  "pourtant", "préalable", "près", "presqu'", "presque", "primo",
  "priori", "prou", "pu", "puis", "puisqu'", "puisque", "Q", "qu'", "qua",
  "quand", "quarante", "quarante-cinq", "quarante-deux",
  "quarante-et-un", "quarante-huit", "quarante-neuf",
  "quarante-quatre", "quarante-sept", "quarante-six",
  "quarante-trois", "quasi", "quatorze", "quatre", "quatre-vingt",
  "quatre-vingt-cinq", "quatre-vingt-deux", "quatre-vingt-dix",
  "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf",
  "quatre-vingt-dix-sept", "quatre-vingt-douze", "quatre-vingt-huit",
  "quatre-vingt-neuf", "quatre-vingt-onze", "quatre-vingt-quatorze",
  "quatre-vingt-quatre", "quatre-vingt-quinze", "quatre-vingts",
  "quatre-vingt-seize", "quatre-vingt-sept", "quatre-vingt-six",
  "quatre-vingt-treize", "quatre-vingt-trois", "quatre-vingt-un",
  "quatre-vingt-une", "que", "quel", "quelle", "quelles", "quelqu'",
  "quelque", "quelquefois", "quelques", "quelques-unes",
  "quelques-uns", "quelqu'un", "quelqu'une", "quels", "qui",
  "quiconque", "quinze", "quoi", "quoiqu'", "quoique", "R", "revoici",
  "revoilà", "rien", "S", "s'", "sa", "sans", "sauf", "se", "secundo",
  "seize", "selon", "sensu", "sept", "septante", "sera", "serai",
  "seraient", "serais", "serait", "seras", "serez", "seriez", "serions",
  "serons", "seront", "ses", "si", "sic", "sine", "sinon", "sitôt",
  "situ", "six", "soi", "soient", "sois", "soit", "soixante",
  "soixante-cinq", "soixante-deux", "soixante-dix",
  "soixante-dix-huit", "soixante-dix-neuf", "soixante-dix-sept",
  "soixante-douze", "soixante-et-onze", "soixante-et-un",
  "soixante-et-une", "soixante-huit", "soixante-neuf",
  "soixante-quatorze", "soixante-quatre", "soixante-quinze",
  "soixante-seize", "soixante-sept", "soixante-six", "soixante-treize",
  "soixante-trois", "sommes", "son", "sont", "soudain", "sous",
  "souvent", "soyez", "soyons", "stricto", "suis", "sur",
  "sur-le-champ", "surtout", "sus", "T", "-t", "t'", "ta", "tacatac",
  "tant", "tantôt", "tard", "te", "tel", "telle", "telles", "tels", "ter",
  "tes", "toi", "-toi", "ton", "tôt", "toujours", "tous", "tout", "toute",
  "toutefois", "toutes", "treize", "trente", "trente-cinq",
  "trente-deux", "trente-et-un", "trente-huit", "trente-neuf",
  "trente-quatre", "trente-sept", "trente-six", "trente-trois", "très",
  "trois", "trop", "tu", "-tu", "U", "un", "une", "unes", "uns", "USD",
  "V", "va", "vais", "vas", "vers", "veut", "veux", "via", "vice-versa",
  "vingt", "vingt-cinq", "vingt-deux", "vingt-huit", "vingt-neuf",
  "vingt-quatre", "vingt-sept", "vingt-six", "vingt-trois",
  "vis-à-vis", "vite", "vitro", "vivo", "voici", "voilà", "voire",
  "volontiers", "vos", "votre", "vous", "-vous", "W", "X", "y", "-y",
  "Z", "zéro"]]

stop_words = set(stop_words)

# translate to lower case, normalize whitespace
# for ease of filtering
# this needs to be a mapping as Unicode strings do not support traditional
# str.translate with a 256-length string
lc_map = {}
punct_map = {}
for c in string.whitespace:
  lc_map[ord(c)] = 32
del lc_map[32]
for c in string.punctuation + '\'\xab\xbb':
  punct_map[ord(c)] = 32
punct_map[0x2019] = "'"

# decode HTML entities with known Unicode equivalents
ent_re = re.compile(r'\&([^;]*);')
def ent_sub(m):
  ent = m.groups()[0]
  if ent in htmlentitydefs.name2codepoint:
    return chr(htmlentitydefs.name2codepoint[ent])
  if ent.startswith('#'):
    if ent.lower().startswith('#x'):
      codepoint = int('0x' + ent[2:], 16)
    else:
      try:
        codepoint = int(ent[1:])
      except ValueError:
        return ent
    if codepoint > 0 and codepoint < sys.maxunicode:
      return chr(codepoint)
  # fallback - leave as-is
  return '&%s;' % ent
  
def decode_entities(s):
  return ent_re.sub(ent_sub, s)

# XXX need to normalize for HTML entities as well
def lower(s):
  """Turn a string lower-case, including stripping accents"""
  return strip_diacritics(decode_entities(s)).translate(lc_map).lower()

# XXX this implementation is hopefully correct, but inefficient
# XXX we should be able to replace it with a finite state automaton in C
# XXX for better performance
# tested with u=u'\xe9sop\xe9sopfoo\xe9sop' and unicodedata.normalize('NFD', u)
def replace_first(s, pat, mark_begin, mark_end):
  """Case-insensitive replacement of the 1st occurrence of pat in s by repl"""
  lc = lower(s)
  pat = lower(pat)
  start = lc.find(pat)
  if start == -1:
    return s
  else:
    # (c)translitcodec does more than simply lowercasing, so we will need
    # to use bisection to find where in the untransliterated string the
    # pattern can be found
    if lower(s[start:]).find(pat) == -1:
      # As a fast-path, use the position in the transliterated string as
      # an initial guess of where to start, but in this case it did not work
      start = 0
    end = len(s)
    while lower(s[start:]).find(pat) > 0:
      if start == end:
        # XXX still can't find it, this shouldn't happen
        return s
      mid = (start + end + 1) // 2
      if lower(s[mid:]).find(pat) >= 0:
        start = mid
      else:
        end = mid
    # now we have the start, find the end
    end = start + len(pat)
    if lower(s[start:end]) != pat:
      end = start
      # the pattern may not be equal, e.g. searching for 'GB' in '£' that
      # expands to 'gbp'
      while not lower(s[start:end]).startswith(pat):
        end += 1
    return s[:start] + mark_begin + s[start:end] + mark_end + s[end:]

strip_tags_re = re.compile('<[^>]*>')
def get_words(s):
  return set([
    word for word
    in lower(str(strip_tags_re.sub('', str(s)))
             ).translate(punct_map).split()
    if word not in stop_words])
def stem(words):
  return {porter2.stem(word) for word in words}
  
########################################################################
# HTML tag balancing logic
#
# from the HTML4 loose DTD http://www.w3.org/TR/html4/loose.dtd
fontstyle = ('b', 'big', 'i', 's', 'small', 'strike', 'tt', 'u')
phrase = ('abbr', 'acronym', 'cite', 'code', 'dfn', 'em', 'kbd', 'samp',
          'strong', 'var')
heading = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
html4_elts = ('a', 'address', 'applet', 'area', 'base', 'basefont', 'bdo',
              'blockquote', 'body', 'br', 'button', 'caption', 'center',
              'col', 'colgroup', 'dd', 'del', 'dir', 'div', 'dl', 'dt',
              'fieldset', 'font', 'form', 'frame', 'frameset', 'head', 'hr',
              'html', 'iframe', 'img', 'input', 'ins', 'isindex', 'label',
              'legend', 'li', 'link', 'map', 'menu', 'meta', 'noframes',
              'noscript', 'object', 'ol', 'optgroup', 'option', 'p', 'param',
              'pre', 'q', 'script', 'select', 'span', 'style', 'sub', 'sup',
              'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead',
              'title', 'tr', 'ul') + fontstyle + phrase + heading
inline_elts = ('a', 'abbr', 'acronym', 'address', 'bdo', 'caption', 'cite',
               'code', 'dfn', 'dt', 'em', 'font', 'i',
               'iframe', 'kbd', 'label', 'legend', 'p', 'pre', 'q', 's',
               'samp', 'small', 'span', 'strike', 'strong', 'sub', 'sup',
               'tt', 'u', 'var') + fontstyle + phrase + heading
# strictly speaking the closing '</p> tag is optional, but let's close it
# since it is so common
closing = ('a', 'address', 'applet', 'bdo', 'blockquote', 'button', 'caption',
           'center', 'del', 'dir', 'div', 'dl', 'fieldset', 'font', 'form',
           'frameset', 'iframe', 'ins', 'label', 'legend', 'map', 'menu',
           'noframes', 'noscript', 'object', 'ol', 'optgroup', 'pre', 'q',
           'script', 'select', 'span', 'style', 'sub', 'sup', 'table',
           'textarea', 'title', 'ul') + fontstyle + phrase + heading + ('p',)
# <!ENTITY % block
block = ('address', 'blockquote', 'center', 'dir', 'div', 'dl', 'fieldset',
         'form', 'hr', 'isindex', 'menu', 'noframes', 'noscript', 'ol', 'p',
         'pre', 'table', 'ul') + heading
# for XSS attacks, as feedparser is not completely immune
banned = ('script', 'applet', 'style')
# speed up things a bit
block = set(block)
closing = set(closing)
banned = set(banned)

acceptable_elements = set([
  'a', 'abbr', 'acronym', 'address', 'area', 'article', 'aside', 'audio', 'b',
  'big', 'blockquote', 'br', 'button', 'canvas', 'caption', 'center', 'cite',
  'code', 'col', 'colgroup', 'command', 'datagrid', 'datalist', 'dd', 'del',
  'details', 'dfn', 'dialog', 'dir', 'div', 'dl', 'dt', 'em', 'event-source',
  'fieldset', 'figcaption', 'figure', 'footer', 'font', 'form', 'header',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input', 'ins',
  'keygen', 'kbd', 'label', 'legend', 'li', 'm', 'map', 'menu', 'meter',
  'multicol', 'nav', 'nextid', 'ol', 'output', 'optgroup', 'option', 'p',
  'pre', 'progress', 'q', 's', 'samp', 'section', 'select', 'small', 'sound',
  'source', 'spacer', 'span', 'strike', 'strong', 'sub', 'sup', 'table',
  'tbody', 'td', 'textarea', 'time', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u',
  'ul', 'var', 'video', 'noscript'
])

acceptable_attributes = [
  'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align', 'alt',
  'autocomplete', 'autofocus', 'axis', 'background', 'balance', 'bgcolor',
  'bgproperties', 'border', 'bordercolor', 'bordercolordark',
  'bordercolorlight', 'bottompadding', 'cellpadding', 'cellspacing', 'ch',
  'challenge', 'char', 'charoff', 'choff', 'charset', 'checked', 'cite',
  'class', 'clear', 'color', 'cols', 'colspan', 'compact', 'contenteditable',
  'controls', 'coords', 'data', 'datafld', 'datapagesize', 'datasrc',
  'datetime', 'default', 'delay', 'dir', 'disabled', 'draggable', 'dynsrc',
  'enctype', 'end', 'face', 'for', 'form', 'frame', 'galleryimg', 'gutter',
  'headers', 'height', 'hidefocus', 'hidden', 'high', 'href', 'hreflang',
  'hspace', 'icon', 'id', 'inputmode', 'ismap', 'keytype', 'label',
  'leftspacing', 'lang', 'list', 'longdesc', 'loop', 'loopcount', 'loopend',
  'loopstart', 'low', 'lowsrc', 'max', 'maxlength', 'media', 'method', 'min',
  'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'open', 'optimum',
  'pattern', 'ping', 'point-size', 'poster', 'pqg', 'preload', 'prompt',
  'radiogroup', 'readonly', 'rel', 'repeat-max', 'repeat-min', 'replace',
  'required', 'rev', 'rightspacing', 'rows', 'rowspan', 'rules', 'scope',
  'selected', 'shape', 'size', 'span', 'src', 'start', 'step', 'summary',
  'suppress', 'tabindex', 'target', 'template', 'title', 'toppadding', 'type',
  'unselectable', 'usemap', 'urn', 'valign', 'value', 'variable', 'volume',
  'vspace', 'vrml', 'width', 'wrap'
]

acceptable_css_properties = [
  'azimuth', 'background-color', 'border-bottom-color', 'border-collapse',
  'border-color', 'border-left-color', 'border-right-color',
  'border-top-color', 'clear', 'color', 'cursor', 'direction', 'display',
  'elevation', 'float', 'font', 'font-family', 'font-size', 'font-style',
  'font-variant', 'font-weight', 'height', 'letter-spacing', 'line-height',
  'overflow', 'pause', 'pause-after', 'pause-before', 'pitch', 'pitch-range',
  'richness', 'speak', 'speak-header', 'speak-numeral', 'speak-punctuation',
  'speech-rate', 'stress', 'text-align', 'text-decoration', 'text-indent',
  'unicode-bidi', 'vertical-align', 'voice-family', 'volume', 'white-space',
  'width'
]

def sanitize_text(text):
  """Sanitize text fields like title or feed description for XSS"""
  return bleach.clean(
    text,
    tags=[],
    attributes=[],
    styles=[],
    strip=True
  )
  

tag_re = re.compile(r'(<>|<[^!].*?>|<!\[CDATA\[|\]\]>|<!--.*?-->|<[!]>)',
                    re.DOTALL | re.MULTILINE)
def balance(html, limit_words=None, ellipsis=' ...'):
  # we cannot trust feedparser to sanitize
  if not limit_words:
    #return html5lib.serialize(html5lib.parse(html))
    return bleach.clean(
      html,
      tags=acceptable_elements,
      attributes=acceptable_attributes,
      styles=acceptable_css_properties,
      strip=True
    )

  # the legacy balancing logic is redundant with Bleach's,
  # but this is seldom used
  word_count = 0
  tokens = tag_re.split(html)
  out = []
  stack = []
  for token in tokens:
    if not token.startswith('<'):
      if limit_words and word_count > limit_words:
        break
      words = token.split()
      word_count += len(words)
      if limit_words and word_count > limit_words:
        crop = limit_words - word_count
        out.append(' '.join(words[:crop]) + ellipsis)
      else:
        out.append(token)
      continue
    if token.startswith('<!'): continue
    if token == ']]>': continue
    if not token.endswith('>'): continue # invalid
    element = token[1:-1].split()[0].lower()
    if not element: continue # invalid
    if element in banned:
      element = 'pre'
      token = '<pre>'

    if element.startswith('/'):
      element = element[1:]
      if element in banned:
        element = 'pre'
        token = '</pre>'
      if element in stack:
        top = None
        while stack and top != element:
          top = stack.pop()
          out.append('</%s>' % top)
        continue
      else:
        continue

    if element in block and stack and stack[-1] not in block:
      # close previous block if any
      for i in range(len(stack) - 1, -1, -1):
        if stack[i] in block: break
      stack, previous_block = stack[:i], stack[i:]
      previous_block.reverse()
      for tag in previous_block:
        out.append('</%s>' % tag)
      
    if element in closing and not token.endswith('/>'):
      stack.append(element)
    out.append(token)
  # flush the stack
  out.extend(['</%s>' % element for element in reversed(stack)])
  html = ''.join(out)
  return bleach.clean(
    html,
    tags=acceptable_elements,
    attributes=acceptable_attributes,
    styles=acceptable_css_properties,
    strip=True
  )

########################################################################
def normalize_all(f):
  normalize_feed(f)
  for item in f.entries:
    normalize(item, f)

def normalize_feed(f):
  if 'description' not in f['channel']:
    f['channel']['description'] = f['channel'].get('title', '')
  f['channel']['description'] = sanitize_text(f['channel']['description'])
  if 'modified' in f and type(f['modified']) == str:
    try:
      f['modified'] = time.strptime(f['modified'],
                                    '%a, %d %b %Y %H:%M:%S GMT')
    except ValueError:
      f['modified'] = time.strptime(f['modified'],
                                    '%a, %d %b %Y %H:%M:%S +0000')

# Often, broken RSS writers will not handle daylight savings time correctly
# and use a timezone that is off by one hour. For instance, in the US/Pacific
# time zone:
# February 3, 2004, 5:30PM is 2004-02-03T17:30:00-08:00 (standard time)
# August 3, 2004, 5:30PM US/Pacific is 2004-08-03T17:30:00-07:00 (DST)
# but broken implementations will incorrectly write:
# 2004-08-03T17:30:00-08:00 in the second case
# There is no real good way to ward against this, but if the created or
# modified date is in the future, we are clearly in this situation and
# substract one hour to correct for this bug
def fix_date(date_tuple):
  if not date_tuple:
    return date_tuple
  if date_tuple > time.gmtime():
    # feedparser's parsed date tuple has no DST indication, we need to force it
    # because there is no UTC equivalent of mktime()
    date_tuple = date_tuple[:-1] + (-1,)
    date_tuple = time.localtime(time.mktime(date_tuple) - 3600)
    # if it is still in the future, the implementation is hopelessly broken,
    # truncate it to the present
    if date_tuple > time.gmtime():
      return time.gmtime()
    else:
      return date_tuple
  else:
    return date_tuple

# why doesn't feedparser do these basic normalizations?
def basic(f, feed_xml):
  if 'url' not in f:
    f['url'] = feed_xml
  # CVS versions of feedparser are not throwing exceptions as they should
  # see:
  # http://sourceforge.net/tracker/index.php?func=detail&aid=1379172&group_id=112328&atid=661937
  if not f.feed or ('link' not in f.feed or 'title' not in f.feed):
    # some feeds have multiple links, one for self and one for PuSH
    if f.feed and 'link' not in f.feed and 'links' in f.feed:
      try:
        for l in f.feed['links']:
          if l['rel'] == 'self':
            f.feed['link'] = l['href']
      except KeyError:
        pass
  if 'title' in f.feed:
    f.feed['title'] = sanitize_text(f.feed['title'])
  
def dereference(url, seen=None, level=0):
  """Recursively dereference a URL"""
  # this set is used to detect redirection loops
  if seen is None:
    seen = set([url])
  else:
    seen.add(url)
  # stop recursion if it is too deep
  if level > 16:
    return url
  try:
    r = requests.get(url, allow_redirects=False, timeout=param.http_timeout)
    if not r.is_redirect:
      return url
    else:
      # break a redirection loop if it occurs
      redir = r.headers.get('Location')
      if True not in [redir.startswith(p)
                      for p in ['http://', 'https://', 'ftp://']]:
        return url
      if redir in seen:
        return url
      # some servers redirect to Unicode URLs, which are not legal
      try:
        str(redir)
      except UnicodeDecodeError:
        return url
      # there might be several levels of redirection
      return dereference(redir, seen, level + 1)
  except (requests.exceptions.RequestException, ValueError, socket.error):
    return url
  except:
    util.print_stack()
    return url
  
url_re = re.compile('(?:href|src)="([^"]*)"', re.IGNORECASE)

def normalize(item, f, run_filters=True):
  # get rid of RDF lossage...
  for key in ['title', 'link', 'created', 'modified', 'author',
              'content', 'content_encoded', 'description']:
    if type(item.get(key)) == list:
      if len(item[key]) == 1:
        item[key] = item[key][0]
      else:
        candidate = [i for i in item[key] if i.get('type') == 'text/html']
        if len(candidate) > 1 and key == 'content':
          candidate = sorted(candidate,
                             key=lambda i: len(i.get('value', '')),
                             reverse=True)[:1]
        if len(candidate) == 1:
          item[key] = candidate[0]
        else:
          # XXX not really sure how to handle these cases
          print('E' * 16, 'ambiguous RDF', key, item[key], file=param.log)
          item[key] = item[key][0]
    if isinstance(item.get(key), dict) and 'value' in item[key]:
      item[key] = item[key]['value']
  ########################################################################
  # title
  if 'title' not in item or not item['title'].strip():
    item['title'] = 'Untitled'
  item['title'] = sanitize_text(item['title'])
  item['title_lc'] =   lower(item['title'])
  item['title_words_exact'] =  get_words(item['title_lc'])
  item['title_words'] =  stem(item['title_words_exact'])
  ########################################################################
  # link
  #
  # The RSS 2.0 specification allows items not to have a link if the entry
  # is complete in itself
  # that said this is almost always spurious, so we filter it below
  if 'link' not in item:
    item['link'] = f['channel']['link']
    # We have to be careful not to assign a default URL as the GUID
    # otherwise only one item will ever be recorded
    if 'id' not in item:
      item['id'] = 'HASH_CONTENT'
      item['RUNT'] = True
  ########################################################################
  # GUID
  if 'id' not in item:
    item['id'] = item['link']
  ########################################################################
  # creator
  if 'author' not in item or item['author'] == 'Unknown':
    item['author'] = 'Unknown'
    if 'author' in f['channel']:
      item['author'] = f['channel']['author']
  item['author'] = sanitize_text(item['author'])
  ########################################################################
  # created amd modified dates
  if 'modified' not in item:
    item['modified'] = f['channel'].get('modified')
  # created - use modified if not available
  if 'created' not in item:
    if 'modified_parsed' in item:
      created = item['modified_parsed']
    else:
      created = None
  else:
    created = item['created_parsed']
  if not created:
    # XXX use HTTP last-modified date here
    created = time.gmtime()
    # feeds that do not have timestamps cannot be garbage-collected
    # XXX need to find a better heuristic, as high-volume sites such as
    # XXX The Guardian, CNET.com or Salon.com lack item-level timestamps
    f['oldest'] = '1970-01-01 00:00:00'
  created = fix_date(created)
  item['created'] = time.strftime(date_fmt, created)
  # keep track of the oldest item still in the feed file
  if 'oldest' not in f:
    f['oldest'] = '9999-99-99 99:99:99'
  if item['created'] < f['oldest']:
    f['oldest'] = item['created']
  # finish modified date
  if 'modified_parsed' in item and item['modified_parsed']:
    modified = fix_date(item['modified_parsed'])
    # add a fudge factor time window within which modifications are not
    # counted as such, 10 minutes here
    if not modified or abs(time.mktime(modified) - time.mktime(created)) < 600:
      item['modified'] = None
    else:
      item['modified'] = time.strftime(date_fmt, modified)
  else:
    item['modified'] = None
  ########################################################################
  # content
  if 'content' in item:
    content = item['content']
  elif 'content_encoded' in item:
    content = item['content_encoded']
  elif 'description' in item:
    content = item['description']
  else:
    content = '<a href="' + item['link'] + '">' + item['title'] + '</a>'
  if not content:
    content = '<a href="' + item['link'] + '">' + item['title'] + '</a>'
  # strip embedded NULs as a defensive measure
  content = content.replace('\0', '')
  # apply ad filters and other degunking to content
  old_content = None
  while old_content != content:
    old_content = content
    try:
      for filter in transform.filter_list:
        content = filter.apply(content, f, item)
    except:
      util.print_stack(black_list=['item'])
  # balance tags like <b>...</b> and sanitize
  content = balance(content)
  content_lc = lower(content)
  # the content might have invalid 8-bit characters.
  # Heuristic suggested by Georg Bauer
  if type(content) != str:
    try:
      content = content.decode('utf-8')
    except UnicodeError:
      content = content.decode('iso-8859-1')
  #
  item['content'] = content
  # we recalculate this as content may have changed due to tag rebalancing, etc
  item['content_lc'] = lower(content)
  item['content_words_exact'] = get_words(item['content_lc'])
  item['content_words'] = stem(item['content_words_exact'])
  item['union_lc'] = item['title_lc'] + '\n' + item['content_lc']
  item['union_words'] = item['title_words'].union(item['content_words'])
  item['urls'] = url_re.findall(content)
  ########################################################################
  # categories/tags
  # we used 'category' before, but 'category' and 'categories' are
  # intercepted by feedparser.FeedParserDict.__getitemm__ and treated as
  # special case
  if 'tags' in item and type(item['tags']) == list:
    item['item_tags'] = set([lower(sanitize_text(t['term']))
                             for t in item['tags']])
  else:
    item['item_tags'] = []
  ########################################################################
  # map unicode
  # for key in ['title', 'link', 'created', 'modified', 'author', 'content']:
  #   if type(item.get(key)) == str:
  #     item[key] = item[key].encode('ascii', 'xmlcharrefreplace')
  # hash the content as the GUID if required
  if item['id'] == 'HASH_CONTENT':
    item['id']= hashlib.md5(
      (item['title'] + item['content']).encode('utf-8')).hexdigest()
  return item
  
def escape_xml(s):
  """Escape entities for a XML target"""
  try:
    s = s.decode('utf-8')
  except:
    pass
    
  return s.replace('&', '&amp;').replace("'", "&apos;").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;').encode('ascii', 'xmlcharrefreplace').decode('ascii')
