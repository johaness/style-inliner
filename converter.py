import urllib
import urlparse
import cssutils
from lxml import etree, html


ignore_list = ['html', 'head', 'title', 'meta', 'link', 'script']


def convert(document, css):
    document = html.fromstring(document)
    elms = {} # stores all inlined elements.
    for rule in cssutils.parseString(css):
        for element in document.cssselect(getattr(rule, 'selectorText', [])):
            if element not in elms:
                elms[element] = cssutils.css.CSSStyleDeclaration()
                inline_styles = element.get('style')
                if inline_styles:
                    for p in cssutils.css.CSSStyleDeclaration(cssText=inline_styles):
                        elms[element].setProperty(p)

            for p in rule.style:
                elms[element].setProperty(p.name, p.value, p.priority)

    # Set inline style attributes unless the element is not worth styling.
    for element, style in elms.iteritems():
        if element.tag not in ignore_list:
            element.set('style', style.getCssText(separator=u''))

    return etree.tostring(document, method="xml", pretty_print=True, encoding='UTF-8')
