import urllib.error
import urllib.parse
import urllib.request


def gen(string):
    yield string


def scriptsrc(source):
    return markup('script',
                  attrs={'type': 'text/javascript', 'src': source})


def csssrc(href):
    return markup('link', {
        'rel': 'stylesheet',
        'type': 'text/css',
        'href': href}, '')


def script(scrpt):
    return markup('script',
                  {'type': 'text/javascript'},
                  '//<![CDATA[\n' + scrpt + '\n//]]>')


def openelem(name, attrs=None, closeonstart=False):
    attrs = {} if attrs == None else attrs

    ret = ''
    ret += '<' + name
    for key, val in attrs.items():
        valpart = '' if val == None or val == '' else ('="' + val + '"')
        ret += ' %(att)s%(val)s' % {'att': key, 'val': valpart}
    ret += '/' if closeonstart else ''
    ret += '>'
    return ret


def closeelem(name):
    return '</' + name + '>'


def flatten_gen(generator):
    ret = ''
    for item in generator:
        ret += item
    return ret


def markup_gen(tag, attrs=None, innardsgen=gen(''),
               closetag=True, closeonstart=False):

    attrs = {} if attrs == None else attrs

    yield openelem(tag, attrs, closeonstart)
    for item in innardsgen:
        yield item
    if closetag and not closeonstart:
        yield closeelem(tag)


def markup(tag, attrs=None, innards='', closetag=True, closeonstart=False):
    attrs = {} if attrs == None else attrs
    return flatten_gen(markup_gen(tag, attrs, gen(innards),
                                  closetag, closeonstart))


def voidelem(name, attrs=None):
    attrs = {} if attrs == None else attrs
    return openelem(name, attrs=attrs, closeonstart=True)


def hr():
    return voidelem('hr')


def br():
    return voidelem('br')


def urlencode(base, querydict):
    return base + '?' + urllib.parse.urlencode(querydict)


def geturl(url):
    return urllib.request.urlopen(url).read()


def hyperlink(url, desc):
    return markup('a', attrs={'href': url}, innards=desc)


def div(divid, innards, attrs=None):
    attrs = {} if attrs == None else attrs
    attrs['id'] = divid
    return markup('div', attrs=attrs, innards=innards)


def img(src, width='', height='', cls=''):
    data = {
        'src': src,
        'alt': src
    }
    if cls:
        data['class'] = cls
    if width != '':
        data['width'] = str(width)
    if height != '':
        data['height'] = str(height)
    ret = markup('img', attrs=data, closeonstart=True)
    return ret


def bold(innards):
    return markup('b', innards=innards)


def inputtag(itype, iname, ivalue):
    return markup('input',
                  attrs={
                      'type': itype,
                      'name': iname,
                      'value': ivalue,
                  })


def div_gen(divid, innardsgen):
    for item in markup_gen('div', {'id': divid}, innardsgen):
        yield item


def option(value, desc, selected=False):
    attrs = {'value': value}
    if selected:
        attrs['selected'] = ''
    return markup('option', attrs=attrs, innards=desc)
