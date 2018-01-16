from django.utils.safestring import mark_safe
from django.forms.widgets import MediaDefiningClass
from django.utils.html import conditional_escape, format_html
from django.core.exceptions import ImproperlyConfigured


#! escape?
class HitRendererBase:
    '''
    Render data to look like search engine hits.
    They render as HTML lists.
    HitRenderers escape all to_html() data. They ignore surplus data, 
    and the default templates insert defaults for missing data.
    
    @param element_template Template to use for each element of data
    @param element_attributes Dict to add attributes to each HTML list tag
    '''
    element_template = None
    element_attributes = {}
    
    def __init__(self, element_attrs={}):
        if (self.element_template is None):
            raise ImproperlyConfigured("Hit renderer '{0}' must have a 'element_template' attribute defined.".format(
                self.__class__.__name__
                ))
        if (element_attrs):
            self.element_attributes = element_attrs
        if (self.element_attributes):
            element_attributes_render = self._build_attrs(self.element_attributes) 
        else:
            element_attributes_render = ''
            
        self._row_start = format_html('<li {0}>', element_attributes_render)
        self._row_end = '</li>'

    def _build_attrs(self, attrs):
        b = []         
        for k,v in attrs.items():
            b.append('{0}="{1}"'.format(k, v))
        return ' '.join(b)
    
    def as_html(self, row_data):
        '''
        @param row_data [{}] data in dicts is formatted into the element_template (surplus is ignored)
        '''
        b = []
        for data in row_data:
            row = '{0}{1}{2}'.format(
                self._row_start,
                format_html(self.element_template, **data),
                self._row_end
            )
            b.append(row)
        return mark_safe('\n'.join(b))   
    
    
    
class HitRenderer(HitRendererBase, metaclass=MediaDefiningClass):
    '''
    Render rows of search results with media.
    The action is in as_html. Returns HTML list items only. 
    Must define element_template, a simple string 'format' template.
    '''
    
class HitRendererText(HitRenderer):
    '''
    row_data = [{'url': ..., 'title': ..., 'teaser': ... }]
    '''
    element_template = '<h3><a href="{url}">{title}</a></h3><cite class="url_display">{url}</cite><div class="teaser">{teaser}</div>'
    class Media:
        css = {'screen' : ('need/css/text_hits.css',)}
        
        
class HitRendererImage(HitRenderer):
    '''
    row_data = [{'url': ..., 'src': ...}]
    '''
    element_template = '<a href="{url}"><img src="{src}"></a>'
    class Media:
        css = {'screen' : ('need/css/image_hits.css',)}




class CharfieldGetFormRendererBase:
  #<form {% if id_name %}id="{{ id_name }}_form" {% endif %}class="generic-form" action="{{ submit_url }}" method="post" {% if form.is_multipart %}enctype="multipart/form-data" {% endif %} novalidate>
   # {% csrf_token %},
    submit_url = ''
    template = '<form action="{}" method="get" novalidate>{}</form>'
    form_attrs = {}
    name = None
    value = ''
    placeholder = ''
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            print('setatt:')
            print(k)
            setattr(self, k, v)
        if (not self.name):
            self.__class__.__name__
        if (not self.submit_url):
            raise ImproperlyConfigured("{0} must have a 'submit_url' attribute defined.".format(
                self.__class__.__name__
                ))
                            
    def _build_attrs(self, attrs):
        b = []         
        for k,v in attrs.items():
            b.append('{0}="{1}"'.format(k, v))
        return ' '.join(b)
        
    def to_html(self):  
        #{% if id_name %}id="{{ id_name }}_form" {% endif %}
        input_html = '<input type="text" name="{0}"{1}{2}>'.format(
          self.name if (self.name) else self.__class__.__name__,
          ' value="{}"'.format(self.value) if self.value else '',
          ' placeholder="{}"'.format(self.placeholder) if self.placeholder else '',
          )
          
        o = '<form {} action="{}" method="get" novalidate>{}</form>'.format(
            self._build_attrs(self.form_attrs),
            self.submit_url,
            input_html
            )
        return mark_safe(o)



class CharfieldGetFormRenderer(CharfieldGetFormRendererBase, metaclass=MediaDefiningClass):
    '''
    Render rows of search results with media.
    The action is in as_html. Returns HTML list items only. 
    Must define element_template, a simple string 'format' template.
    '''


class SearchFormRenderer(CharfieldGetFormRenderer):
    '''
    Single box search form.
    GET form with one charfield.
    With pre-defined input configuration and CSS defaults.
    '''
    name = 'search'
    placeholder= "Search"
    
    def __init__(self, **kwargs):
        if (not 'form_attrs' in kwargs):
            kwargs['form_attrs']={'class': 'searchbox tight-searchbox'}
        return super().__init__(**kwargs)

    class Media:
        css = {'screen' : ('need/css/text_input.css',)}
