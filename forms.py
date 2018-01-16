from django.utils.html import conditional_escape #, html_safe
from django.utils.safestring import mark_safe
from django.forms.widgets import MediaDefiningClass



#! base name for classes and name
#! prefix?
class BaseTextInputForm():
    '''
    Djangos formbuild classes are smart, but too complex for a 
    deliberately simple form like a search box. This case needs no 
    instances, no field management, etc.

    This class is a rebuild of Django's Form class. It contains one 
    builtin field only, called 'data'. With only one field it has
    no render options such as to_list() etc. It binds, verifies, errors, 
    and renders like a Django Form, so (in Python) it's a Django Form.
    
    good attrs: required, maxlength, classes, name, placeholder
    '''
    #? prefix is only for Django naespacing of Fields, I think?
    #? does nothing here, but moving towards complete API
    def __init__(self, 
        data=None, 
        prefix=None,
        initial=None, 
        attrs=None
        ):
        '''
        Data when form is bound
        '''
        self.data = data
        self.initial = initial
        self.is_bound = data is not None
        self.error = False
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        
    def __str__(self):
        return self.as_html()
    
    def __repr__(self): 
        return '<{cls} bound={bound} valid={valid}>'.format(
            cls = self.__class__.__name__,
            bound = self.is_bound,
            valid = self.is_valid(),
            )
        return '\n'.join(output)

    def format_value(self):
        v = self.data if self.is_bound else self.initial
        return None if v is None else conditional_escape(v)

    def _build_attrs(self):
        attrs = []
        required = self.attrs.pop('required', None)
        if (required):
            attrs.append('required')          
        for k,v in self.attrs.items():
            attrs.append('{0}="{1}"'.format(k, v))
        return ' '.join(attrs)
        
    def _html_output(self):      
        name = self.attrs.pop('name', None)
        value = self.format_value()
        o = '<input type="search" name="{0}" {1} {2}>'.format(
          name if (name) else self.__class__.__name__,
          'value="{0}"'.format(value) if value else '',
          self._build_attrs()
          )
        return mark_safe(o)
        
    def as_html(self):
        return self._html_output()
        
    def clean(self):
        '''
        Hook for cleaning after basic setup.
        '''
        return self.cleaned_data

    def _data_clean(self):
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = None
        if not self.has_changed():
            return
        self.cleaned_data = self.data.strip()
        try:
            self.clean()
        except ValidationError as e:
            self.error = True

    def is_valid(self):
        """Return True if the form has no errors, or False otherwise."""
        self._data_clean()
        return self.is_bound and not self.error
        
    def has_changed(self):
        # normalize types
        initial_value = initial if self.initial is not None else ''
        data_value = self.data if self.data is not None else ''
        return initial_value != data_value
        


class TextInputForm(BaseTextInputForm, metaclass=MediaDefiningClass):
    '''
    A form with one field only, a text input, with validation and media.
    '''


class SearchForm(TextInputForm):
    '''
    Single box search form.
    With pre-defined input configuration and CSS defaults.
    '''
    def __init__(self, 
        data=None,
        prefix=None,
        initial=None, 
        attrs=None
        ):
        super().__init__(
            data, 
            initial,
            attrs={'name':'search', 'maxlength':'256', 'placeholder':"Search"}
         )
    class Media:
        css = {'screen' : ('need/css/text_input.css',)}
