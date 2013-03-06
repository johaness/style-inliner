import sys

import cssutils
from lxml import etree, html


ignore_list = ['html', 'head', 'title', 'meta', 'link', 'script']


def inline_styles(document, css, pretty=False):
    document = html.fromstring(document)
    elms = {} # stores all inlined elements.
    for rule in cssutils.parseString(css):
        if not hasattr(rule, 'selectorText'):
            continue
        for element in document.cssselect(rule.selectorText):
            if element.tag in ignore_list:
                continue

            if element not in elms:
                elms[element] = cssutils.css.CSSStyleDeclaration()
                inline_styles = element.get('style')
                if inline_styles:
                    for p in cssutils.css.CSSStyleDeclaration(cssText=inline_styles):
                        elms[element].setProperty(p)

            for p in rule.style:
                elms[element].setProperty(p.name, p.value, p.priority)

    for element, style in elms.iteritems():
        element.set('style', style.getCssText(separator=u''))

    return etree.tostring(document, method="xml", pretty_print=pretty, encoding='UTF-8')


def main():
    assert len(sys.argv) == 4, \
            """Usage: inline-styler SOURCE_HTML SOURCE_CSS OUTPUT_HTML"""
    src_html, src_css, out_html = sys.argv[1:4]
    res = inline_styles(file(src_html).read(), file(src_css).read())
    with file(out_html, 'w') as outf:
        outf.write(res)
