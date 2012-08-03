import urllib
import urlparse
import cssutils
from lxml import etree, html

from django.conf import settings


class Converter:
    """
    Converts an HTML document to email compatible inline sytles.
    
    Removes any CSS in <link> or <style> tags an inlines them into the 
    appropriate HTML tags.
    
    Usage::
        html = '...' # Your HTML document here...
        inlined_html = Converter(html).convert()
    """
    
    def __init__(self, document, base_url=None):
        # Attach the original document, the base CSS URL, the aggregated CSS and 
        # the converted HTML so it can be accessed once the converter finishes 
        # rendering the document.
        self.document = html.fromstring(document)
        self.base_url = base_url
        self.aggregated_css = ''
        self.converted_html = ''
    
    def convert(self):
        """
        Takes HTML of a document and inlines any CSS.
        
        Optionally takes a `base_url` which is used to find the contents of 
        any `<link>` elements.
        """
        self.aggregated_css = self._get_aggregated_css()
        self.converted_html = self._inline_css()
        
        return self.converted_html
    
    def _get_aggregated_css(self):
        """
        Takes the document and parses out all the CSS from <link> and <style> 
        elements.
        """
        css = self.aggregated_css
        
        # Retrieve CSS rel links from HTML pasted and aggregate into one string.
        rel_links = 'link[rel=stylesheet],link[rel=StyleSheet],link[rel=STYLESHEET]'
        for element in self.document.cssselect(rel_links):
            try:
                css_path = element.get('href')
                
                # If a base URL was passed, we attempt to find the resources 
                # based off of that URL.
                if base_url:
                    if element.get('href').lower().find('http://', 0) < 0:
                        parsed_url = urlparse.urlparse(base_url)
                        css_path = urlparse.urljoin('%s://%s' % (
                            parsed_url.scheme,
                            parsed_url.hostname,
                        ), css_path)
            
                # Grab the CSS from the URL.
                f = urllib.urlopen(css_path)
                css = css + ''.join(f.read())
            
                # Remove the <link> element from the HTML.
                element.getparent().remove(element)
            
            except:
                raise IOError('The stylesheet %s could not be found' % 
                    element.get("href"))
        
        # Include inline style elements from <style> tags. Go through each 
        # element, grab the CSS and then remove it after.
        style_blocks = 'style,Style,STYLE'
        for element in self.document.cssselect(style_blocks):
            css = css + element.text
            element.getparent().remove(element)
        
        return css
    
    def _inline_css(self):
        """
        Takes the aggregated CSS and inlines it into the HTML.
        """
        
        # Stores all inlined elements.
        elms = {}
        
        # Get all the CSS rules in a dictionary that we can operate on.
        style_rules = cssutils.parseString(self.aggregated_css)
        
        for rule in style_rules:
            
            # Look through all elements that match this CSS selector.
            if hasattr(rule, 'selectorText'):
                
                try:
                    for element in self.document.cssselect(rule.selectorText):
                        
                        # 
                        if element not in elms:
                            elms[element] = cssutils.css.CSSStyleDeclaration()
                            
                            # Add existing inline style if present
                            inline_styles = element.get('style')
                            if inline_styles:
                                inline_styles= cssutils.css.CSSStyleDeclaration(
                                    cssText=inline_styles
                                )
                            else:
                                inline_styles = None
                            if inline_styles:
                                for p in inline_styles:
                                    # Set inline style specificity
                                    elms[element].setProperty(p)
                        
                        # Add the styles to the element.
                        for p in rule.style:
                            if p not in elms[element]:
                                elms[element].setProperty(p.name, p.value, p.priority)
                            else:
                                # sameprio = (p.priority == view[element].getPropertyPriority(p.name))
                                # if not sameprio and bool(p.priority) or (sameprio and selector.specificity >= specificities[element][p.name]):
                                #     # later, more specific or higher prio 
                                elms[element].setProperty(p.name, p.value, p.priority)
                except:
                    # TODO: Need to catch errors like ExpressionError here...
                    pass
        
        # Set inline style attributes unless the element is not worth styling.
        ignore_list = [
            'html',
            'head',
            'title',
            'meta',
            'link',
            'script'
        ]
        for element, style in elms.items():
            if element.tag not in ignore_list:
                css = style.getCssText(separator=u'')
                element.set('style', css)
        
        # Convert tree back to plain a HTML string.
        html = etree.tostring(self.document, method="xml", 
            pretty_print=True, encoding='UTF-8')
        
        return html
    
