import feedparser

def startElementNS(self, name, qname, attrs):
    namespace, localname = name
    lowernamespace = str(namespace or '').lower()
    if lowernamespace.find('backend.userland.com/rss') != -1:
        # match any backend.userland.com namespace
        namespace = 'http://backend.userland.com/rss'
        lowernamespace = namespace
    if qname and qname.find(':') > 0:
        givenprefix = qname.split(':')[0]
    else:
        givenprefix = None
    prefix = self._matchnamespaces.get(lowernamespace, givenprefix)
    # I couldn't care one whit about namespaces,
    # so don't let them throw exceptions
    # if givenprefix and (prefix is None or (prefix == '' and lowernamespace == '')) and givenprefix not in self.namespaces_in_use:
    #     raise UndeclaredNamespace("'%s' is not associated with a namespace" % givenprefix)
    # localname = str(localname).lower()

    # qname implementation is horribly broken in Python 2.1 (it
    # doesn't report any), and slightly broken in Python 2.2 (it
    # doesn't report the xml: namespace). So we match up namespaces
    # with a known list first, and then possibly override them with
    # the qnames the SAX parser gives us (if indeed it gives us any
    # at all).  Thanks to MatejC for helping me test this and
    # tirelessly telling me that it didn't work yet.
    attrsD, self.decls = self.decls, {}
    if localname == 'math' and namespace == 'http://www.w3.org/1998/Math/MathML':
        attrsD['xmlns'] = namespace
    if localname == 'svg' and namespace == 'http://www.w3.org/2000/svg':
        attrsD['xmlns'] = namespace

    if prefix:
        localname = prefix.lower() + ':' + localname
    elif namespace and not qname:  # Expat
        for name, value in self.namespaces_in_use.items():
            if name and value == namespace:
                localname = name + ':' + localname
                break

    for (namespace, attrlocalname), attrvalue in attrs.items():
        lowernamespace = (namespace or '').lower()
        prefix = self._matchnamespaces.get(lowernamespace, '')
        if prefix:
            attrlocalname = prefix + ':' + attrlocalname
        attrsD[str(attrlocalname).lower()] = attrvalue
    for qname in attrs.getQNames():
        attrsD[str(qname).lower()] = attrs.getValueByQName(qname)
    localname = str(localname).lower()
    self.unknown_starttag(localname, list(attrsD.items()))

feedparser.parsers.strict._StrictFeedParser.startElementNS = startElementNS
