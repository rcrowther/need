Need
====
Need is an Django API for the Whoosh queryable index builder.  The app joins Django to Whoosh with an interface close to Django itself (a mix of Model and Form styles). It can accept documents in many forms.



Alternatives
------------
Django-Woosh_ has existed for years with no issues. Much lighter weight than this app. Auto-inserts against the primary key. Works by adding a new manager to models to be indexed.

Some people do not like Whoosh because it is slow. Programs that interface C code to Python, for example Xapian_, can be faster. Must be mentioned; Haystack_, which fronts several engines, including Whoosh and Xapian, into one Python/Django API. There is a comparison to these apps below.




Installing the Whoosh module
----------------------------
Install Whoosh code. Probably, ::

    pip3 whoosh

In settings.py, declare the app, ::

    INSTALLED_APPS = [
        'whoosh.apps.WhooshConfig',
    ]

and declare a file route where indexes will be stored, ::

    WHOOSH = os.path.join(BASE_DIR, 'wooshdb')




Building Need into Django
-------------------------
This application will not touch existing models. 

Pick an app with models to include in Whoosh. Create a file 'need.py'. Put this, adjusted for your model, into the file, ::
    
    from need.need import ModelNeed,
    from .models import Firework

    class FireworkNeed(ModelNeed):
       name=TextField(stored=True, field_boost=2.0)
       effect=IdField()
       make=IdField(stored=True)
    
       class Meta:
         need_index = 'firework'
         model = Firework
         fields = ['name', 'description', 'effect', 'make']
  
Note that this class is not intended to be instanciated. 

Fields
~~~~~~
The fields declare how Need will save data. They are similar to Whoosh fields, and accept the same parameters. But they are lower-cased, and a handful of specific numeric types exist, ::

    IntField
    Longfield
    Floatfield.

One note, if you do not set 'stored=True' on a field, you will not be able to search on the field.


The pk field
~~~~~~~~~~~~
The Model version of the Need classes (see below) will automatically include the pk field. If the class cannot default how to Whoosh schema the field (you changed from the default AutoField) the class will complain at runtime. You need to declare a field to explain how the pk field in the model should be represented by a Whoosh schema.
 
Meta
~~~~~
The Meta is where you store any of the options for how this Whoosh index will work. 


Paths
+++++
The meta can accept a 'need_index' parameter which is an override of other computation. The index will be at 'settings.WHOOSH + need_index'  (for the above, 'wooshdb/firework')

The meta can be given an 'app_label' parameter. The index will be stored in 'settings.WHOOSH + app_label _ class_name' (for the above with app_label = 'dragon', 'wooshdb/dragon_firework').

Or no statement can be made, and Need will try to join the application name to the model name (for the above, 'wooshdb/dragon_firework').


How final fields are decided
++++++++++++++++++++++++++++
First, the 'fields' select the fields. Then the declarations decide how they are to be rendered. If the declarations are absent, the class scans the model and tries to guess what the field could be. This may work, but fairly often, the class will refuse to index the data. In which case, make an explicit declaration.


Non-Model Need
~~~~~~~~~~~~~~~~
A much freer API is available which is not conneted to Models. It inherits from models.Need, ::


    from need.models import Need
    
    class FireworkNeed(Need):
       ...
  
This api has no need for a model declaration. 'fields' is still required, but takes information from declared statements only. If field entries do not match a declaration, they will fail, ::

    from need.models import Need
    
    class FireworkNeed(Need):
       title = TextField(stored=True)
       class Meta:
           fields = ['title', 'description']
     
Here, 'description' fails because no field exists to describe it.

If you use this API, it is your responsibility to make decisions about what to store where. For some cases, you may prefer this.

 
Going further
-------------
There is huge depth to the capabilities of gathering data for a Whoosh index.

Introductory material,
    https://whoosh.readthedocs.io/en/latest/schema.html


Managers
--------
Need (Woosh) indexes must be maintained. You must put data into them. This is done via a manager.

Like Django's Models, Need classes are manipulated by a manager. Managers can be written and added to Need classes in the same way as they are to Models. The access attribute is called 'actions' (not 'objects').

The managers available are only the start of what is possible with Need and Whoosh,

+ Manager
+ ManagerManager
+ BlockingManager
+ BlockingManagerManager

The default is Manager. The blocking versions are for multi-threading, discussed later.

Manager offers a simple CRUD interface,

- bulk_add(it)
- add(**fields)
- bulk_delete(fieldname, text)
- merge(**fields)
- read(field, query, callback)
- size(self)

So, ::

    from firework.need import *
 
    FireworkNeed.actions.add(id='0', name='Flower Rocket', effect='Flower-final drooping splay', make='NobelExplosives')

Or, ::

    o = Review.objects.values_list('id', 'name', 'effect', 'make')
    ReviewNeed.actions.bulk_add(o)

Another method is available, this only makes sense for ModelNeed, where a pk field is defined (on a Need class manager, this method will throw an error), ::
 
    delete(key)



The ManagerManager managers might be defined in a Need class like this, ::
    
    ...
    from whoosh.managers import ManagerManager
    
    class FireworkNeed(ModelNeed):
       ...
       manager = ManagerManager()
       class Meta:
         ...
  
ManagerManager managers offer methods probably useful only for admin, currently, :: 

        clear()
        optimize()



Auto-edits
~~~~~~~~~~
TODO: signals


Making queries - read()
~~~~~~~~~~~~~~~~~~~~~~~
The builtin managers offer the most basic possibility for reading, ::

    read(field, query, callback)

So, ::

    FireworkNeed.actions.read('author', 'fred', lambda x : print(str(x)))

The parser used is whoosh.qparser.SimpleParser, which is like most people expect of a general search engine. It handles '-', quoted literals, and uses OR logic for multiple terms.

Currently, the app is not good at exposing Whoosh abilities at querying. I've not wanted to add much to a general search engine interface https://whoosh.readthedocs.io/en/latest/searching.html. No stemming/variations, https://whoosh.readthedocs.io/en/latest/stemming.html. However, there is spell correction, https://whoosh.readthedocs.io/en/latest/spelling.html



Rendering Need classes as forms and results
-------------------------------------------
The need app contains code to help render search forms and results.


List - a hits listing
~~~~~~~~~~~~~~~~~~~~~
A quick list of results from a Need e.g. ::

    from need import List
    from .need import FireworkNeed

    class FireworkSearchList(List):
        need = FireworkNeed
        search_fields = 'title'

    def indexdata_to_renderdata(self, result):
        return {'url' : "/fireworks/{}".format(result['id']), 'title': result['title'], 'teaser': result['description']}
    
Internally, this uses some code called HitRendererText(). This code is described in detail below. Also, the tricky-looking indexdata_to_renderdata() method is mapping search results to what the template will use (a limited context manager). In this case, we are defaulting most items. It doesn't care too much what they are, or what part of the search results are used, as long as the keys are there.

The List class can be overriden in most ways, the Need, the template, the renderer, the CSS, etc. But go ahead, try the view. In urls.py, ::
    
    url(r'^list$', views.FireworkSearchList.as_view(), name='list')

The view works from a query. The keyword is 'search'. So try some url like, ::

    fireworks/list?search=banger
    
Should return a string of results, rendered in the same way as a general search-engine.



SearchHitView
~~~~~~~~~~~~~

Typical code, ::

    from need import SearchHitView
    from .need import FireworkNeed
    
    class FireworkSearchHitView(SearchHitView):
        need = FireworkNeed
        search_fields = 'title'
    
        def indexdata_to_renderdata(self, result):
            return {'url' : "/firework/{}".format(result['id']), 'title': result['title'], 'teaser': 'forgot to store'}


Options
+++++++

need
    Required.

search_fields
    Required. Which fields to search in the index (as declared in the Need (model))

form
    The default is SearchForm, a customised TextInputForm (see below). but anythin that can deliver a 'search' attribute into a GET query.

renderer 
    The default is a HitRendererText.
    
template
    For the hits?

page_count
    The template paginates...(how?)
    
    
    
HitRenderer
~~~~~~~~~~~
HitRenderer is a class-based renderer for Need results. It takes a Need result set and writes HTML. The code has defaults and CSS to write HTML in a form recognisable from several search engines. It also escapes all data, marks output as safe, and detects errors. The base is not special, could write any preformatted HTML.

HitRenderer will take a media class. This is handy, but the media must be mixed into the context to appear in templates (SearchHitView does this automatically).

Has two subclasses, HitRendererText and HitRendererImage. When as_html() is called on them, they expect a list of dicts (or similar structure).

HitRendererText expects, ::

    [ {'title', 'url' (link to...), 'teaser' (short piece of text)} ...]

HitRendererImage expects, ::

    [{'url' (link to...), 'src' (of image)} ...]

HitRenderers ignore surplus data, and will insert defaults for missing data.

Options
+++++++

element_template
    Template to use

element_attributes
    Dict to add attributes to each HTML list tag
    
Prebuilt Forms
++++++++++++++

TextInputForm
_____________
Djangos formbuild classes are smart, but too complex for a deliberately simple form like a search box. This case needs no instances, no field management, etc. 

This is a rebuild of Django's Form class. It contains one builtin field only, called 'data'. It binds, verifies, errors, and renders like a Django Form, so (in Python) it's a Django Form.

SearchForm
__________
A TextInputForm with the name 'search', a placeholder 'Search', and some CSS to look similar to a search engine searchbox.

Insert by ...


In-page form renderers
______________________
When implementing a search box, many site designs try to improve user experience by placing the search box into the middel of another page, or in navigation bars. This is because some form of search, if implemented, should be available on the first possible pages.  

CharfieldGetFormRenderer

SearchFormRenderer

.. _Xapian: https://xapian.org/
.. _Haystack: http://haystacksearch.org/
.. _Django-Woosh: https://github.com/JoeGermuska/django-whoosh/blob/master/django_whoosh/managers.py
