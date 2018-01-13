from django.shortcuts import render
#from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import TemplateView, View

from django.core.exceptions import ImproperlyConfigured
from ..forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..renderers import HitRendererText



class SearchHitView(View):
    need = None
    search_fields = ''
    form = SearchForm
    renderer = HitRendererText()
    template = 'need/search_hits.html'
    page_count = 25
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (self.need is None):
            raise ImproperlyConfigured("Model view search '{0}' must have a Need class defined.".format(
                self.__class__.__name__
                ))
        if (not self.search_fields):
            raise ImproperlyConfigured("Model view search '{0}' must have a 'search_fields' attribute defined.".format(
                self.__class__.__name__
                ))
                
    def indexdata_to_renderdata(self, result):
        ''' Hook for processing generic results before template'''
        return result

        
    def get(self, request, *args, **kwargs):
        def build_results(results):
            for r in results:
               hit_data.append(self.indexdata_to_renderdata(r))
               
        hits = ''
        page = request.GET.get('page')
        query = request.GET.get('search', None)
        if query:
            hit_data = []
            self.need.actions.read(self.search_fields, query, build_results)
            
            pg = Paginator(hit_data, self.page_count)
            try:
                xo = pg.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                xo = pg.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                xo = pg.page(pg.num_pages)
            #! these need to go to template
            prv =  xo.previous_page_number if (xo.has_previous) else None
            nxt =  xo.next_page_number if (xo.has_next) else None
            
            hits = self.renderer.as_html(xo)
        form = self.form(initial=query)
        return render(request, self.template, {'media': form.media + self.renderer.media, 'form': form, 'hits': hits})          
         
         
         
class List(View):
    '''
    View to handle incoming GETs, with information delivered by query.
    Builtin one page template.
    '''
    need = None
    search_fields = ''
    renderer = HitRendererText()
    template = 'need/hits_list.html'
    page_count = 25

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (self.need is None):
            raise ImproperlyConfigured("Model view search '{0}' must have a Need class defined.".format(
                self.__class__.__name__
                ))
        if (not self.search_fields):
            raise ImproperlyConfigured("Model view search '{0}' must have a 'search_fields' attribute defined.".format(
                self.__class__.__name__
                ))

    def indexdata_to_renderdata(self, result):
        ''' Hook for processing generic results before template'''
        return result
        
    def get(self, request, *args, **kwargs):
        def build_results(results):
            for r in results:
               hit_data.append(self.indexdata_to_renderdata(r))
               
        hits = ''
        page = request.GET.get('page')
        query = request.GET.get('search', None)
        if query:
            hit_data = []
            self.need.actions.read(self.search_fields, query, build_results)

            pg = Paginator(hit_data, self.page_count)
            try:
                xo = pg.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                xo = pg.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                xo = pg.page(pg.num_pages)

            #! these need to go to template
            prv =  xo.previous_page_number if (xo.has_previous) else None
            nxt =  xo.next_page_number if (xo.has_next) else None
            
            hits = self.renderer.as_html(xo)
        return render(request, self.template, {'media': self.renderer.media, 'hits': hits})          

