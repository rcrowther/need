from django.shortcuts import render
#from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import TemplateView, View

from django.core.exceptions import ImproperlyConfigured
from ..forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..renderers import HitRendererText


class HitsMixin():         
    need = None
    search_fields = ''         
    renderer = HitRendererText()
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
        
    def get_hits_context(self, kwargs, query, page):
        def build_results(results):
            for r in results:
               hit_data.append(self.indexdata_to_renderdata(r))
               
        hits = ''
        prv = None
        nxt = None
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
            if (xo.has_previous()):
                prv =  xo.previous_page_number()
            if (xo.has_next()):
                nxt =  xo.next_page_number()
            
            hits = self.renderer.as_html(xo)
        kwargs['hits'] = hits
        kwargs['prev_page'] = prv
        kwargs['next_page'] = nxt
        return (hits, prv, nxt)
                           
              
              
                                     
class SearchHitView(TemplateView, HitsMixin):
    #need = None
    #search_fields = ''
    form = SearchForm
    #renderer = HitRendererText()
    template_name = 'need/search_hits.html'
    #page_count = 25
    
    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)
        #if (self.need is None):
            #raise ImproperlyConfigured("Model view search '{0}' must have a Need class defined.".format(
                #self.__class__.__name__
                #))
        #if (not self.search_fields):
            #raise ImproperlyConfigured("Model view search '{0}' must have a 'search_fields' attribute defined.".format(
                #self.__class__.__name__
                #))

         
    #def indexdata_to_renderdata(self, result):
        #''' Hook for processing generic results before template'''
        #return result

        
    #def get(self, request, *args, **kwargs):
        #def build_results(results):
            #for r in results:
               #hit_data.append(self.indexdata_to_renderdata(r))
               
        #hits = ''
        #page = request.GET.get('page')
        #query = request.GET.get('search', None)
        #if query:
            #hit_data = []
            #self.need.actions.read(self.search_fields, query, build_results)
            
            #pg = Paginator(hit_data, self.page_count)
            #try:
                #xo = pg.page(page)
            #except PageNotAnInteger:
                ## If page is not an integer, deliver first page.
                #xo = pg.page(1)
            #except EmptyPage:
                ## If page is out of range (e.g. 9999), deliver last page of results.
                #xo = pg.page(pg.num_pages)
            ##! these need to go to template
            #prv =  xo.previous_page_number if (xo.has_previous) else None
            #nxt =  xo.next_page_number if (xo.has_next) else None
            
            #hits = self.renderer.as_html(xo)
        #form = self.form(initial=query)
        #return render(request, self.template, {'media': form.media + self.renderer.media, 'form': form, 'hits': hits})          

    #def get_context_data(self, **kwargs):
        #def build_results(results):
            #for r in results:
               #hit_data.append(self.indexdata_to_renderdata(r))
               
        #hits = ''
        #prv = None
        #nxt = None
        #page = self.request.GET.get('page')
        #query = self.request.GET.get('search', None)
        #if query:
            #hit_data = []
            #self.need.actions.read(self.search_fields, query, build_results)

            #pg = Paginator(hit_data, self.page_count)
            #try:
                #xo = pg.page(page)
            #except PageNotAnInteger:
                ## If page is not an integer, deliver first page.
                #xo = pg.page(1)
            #except EmptyPage:
                ## If page is out of range (e.g. 9999), deliver last page of results.
                #xo = pg.page(pg.num_pages)

            ##! these need to go to template
            #if (xo.has_previous()):
                #prv =  xo.previous_page_number()
            #if (xo.has_next()):
                #nxt =  xo.next_page_number()
            
            #hits = self.renderer.as_html(xo)
        #media = + self.renderer.media, 
        #if 'media' in kwargs:
            #kwargs['media'] = kwargs['media'] + form.media + self.renderer.media
        #else:
            #kwargs['media'] =  form.media + self.renderer.media
        #kwargs['hits'] = hits
        #kwargs['prev_page'] = prv
        #kwargs['next_page'] = nxt
        #kwargs['form'] =  self.form(initial=query)
        #return super().get_context_data(**kwargs)         

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        query = self.request.GET.get('search', None)
        if query:
            self.get_hits_context(kwargs, query, page)
        media = form.media + self.renderer.media
        if 'media' in kwargs:
            kwargs['media'] = kwargs['media'] + media
        else:
            kwargs['media'] =  media
        kwargs['form'] =  self.form(initial=query)
        return super().get_context_data(**kwargs)
        
        
         
class List(TemplateView, HitsMixin):
    '''
    View to handle incoming GETs, with information delivered by query.
    Builtin one page template.
    '''
    #need = None
    #search_fields = ''
    #renderer = HitRendererText()
    template_name = 'need/hits_list.html'
    #page_count = 25

    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)
        #if (self.need is None):
            #raise ImproperlyConfigured("Model view search '{0}' must have a Need class defined.".format(
                #self.__class__.__name__
                #))
        #if (not self.search_fields):
            #raise ImproperlyConfigured("Model view search '{0}' must have a 'search_fields' attribute defined.".format(
                #self.__class__.__name__
                #))

    #def indexdata_to_renderdata(self, result):
        #''' Hook for processing generic results before template'''
        #return result
        
    #def get(self, request, *args, **kwargs):
        #def build_results(results):
            #for r in results:
               #hit_data.append(self.indexdata_to_renderdata(r))
               
        #hits = ''
        #page = request.GET.get('page')
        #query = request.GET.get('search', None)
        #if query:
            #hit_data = []
            #self.need.actions.read(self.search_fields, query, build_results)

            #pg = Paginator(hit_data, self.page_count)
            #try:
                #xo = pg.page(page)
            #except PageNotAnInteger:
                ## If page is not an integer, deliver first page.
                #xo = pg.page(1)
            #except EmptyPage:
                ## If page is out of range (e.g. 9999), deliver last page of results.
                #xo = pg.page(pg.num_pages)

            ##! these need to go to template
            #prv =  xo.previous_page_number if (xo.has_previous) else None
            #nxt =  xo.next_page_number if (xo.has_next) else None
            
            #hits = self.renderer.as_html(xo)
        #return render(request, self.template, {'media': self.renderer.media, 'hits': hits})          

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        query = self.request.GET.get('search', None)
        if query:
            self.get_hits_context(kwargs, query, page)
        if 'media' in kwargs:
            kwargs['media'] = kwargs['media'] + self.renderer.media
        else:
            kwargs['media'] = self.renderer.media
        return super().get_context_data(**kwargs)
