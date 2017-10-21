from django.urls import reverse
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect



from paper.need import PaperNeed

from django import forms

from django.views.generic.base import TemplateView, View
#from django.core.paginator import InvalidPage, Paginator
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from .forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Model form,like academic search?


#!
#class ModelViewSearch(View):
    #'''
    #View to handle incoming GETs, with information delivered by query.
    #Builtin one page template.
    #'''
    #need = None
    #search_fields = ''
    #form = SearchForm
    
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
                

    #def success(self, hits):
        #pass
        
    #def get(self, request, *args, **kwargs):
        #def build_results(results):
            #for r in results:
               #hits.append(r)
               
        #query = request.GET.get('search', None)
        ##print('query:')
        ##print(query)
        #if query:
            #hits = []
            #self.need.actions.read(self.search_fields, query, build_results)
            #if hits:
                #self.success(hits)
        #form = self.form(initial=query)
        #return render(request, 'need/search.html', {'form': form})          


from .renderers import HitRendererText

#! what about zero return
#! message for no return
#! did you mean?
#! why is multiple search fields not working?
#! why is search term working?
#! test rendered form aainst Form rendering
#! template as full path is rough? TemplateView?
#! pagination
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
                 
                    
#################

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


##################################
#! try on a URL

from .forms import SearchForm

def general_search(request):
    if request.method == 'GET':
        query = request.GET.get('search', None)
        print('query:')
        print(query)
        if not query:
            form = SearchForm()
            return render(request, 'need/search.html', {'form': form})
        else:
            # 1. maybe do some pre-validation before we look in the index
            # 2. Get some results  
            # 3. redirect to some hits result page
            return HttpResponseRedirect('/need/list?search=' + query)
    return HttpResponseNotAllowed("HTTP method {0} not allowed on this view".format(request.method))


class PaperSearchHitView(SearchHitView):
    need = PaperNeed
    search_fields = 'title'

    def indexdata_to_renderdata(self, result):
        return {'url' : "/paper/{}".format(result['id']), 'title': result['title'], 'teaser': 'forgot to store'}

from .renderers import HitRendererImage
  
class PaperSearchHitImageView(SearchHitView):
    need = PaperNeed
    search_fields = 'title'
    renderer = HitRendererImage()

    def indexdata_to_renderdata(self, result):
        return {'url' : "/paper/{}".format(result['id']), 'src': "/static/{}.jpg".format(result['id'])}
  
class PaperList(List):
    need = PaperNeed
    search_fields = 'title'

    def indexdata_to_renderdata(self, result):
        return {'url' : "/fireworks/{}".format(result['id']), 'title': result['title'], 'teaser': 'forgot to store'}
