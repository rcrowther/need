Need
====
Need is an Django API for the Whoosh queryable index builder.  The app joins Django to Whoosh with an interface close to Django itself (a mix of Model and Form styles). It can accept documents in many forms.



Alternatives
~~~~~~~~~~~~
Django-Woosh_ has existed for years with no issues. Much lighter weight than this app. Auto-inserts against the primary key. Works by adding a new manager to models to be indexed.

Some people do not like Whoosh because it is slow. Programs that interface c code to Python, for example Xapian_, can be faster. Also worth mentioning is Haystack_, which fronts several engines, including Whoosh and Xapian, into one Python/Django API. There is a comparison to these apps below.




Installing the Whoosh module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Install Whoosh code. Probably,:

    pip3 whoosh

In settings.py, declare the app,:

    INSTALLED_APPS = [
        'whoosh.apps.WhooshConfig',
    ]

and declare a file route where indexes will be stored,:

    WHOOSH = os.path.join(BASE_DIR, 'wooshdb')



.. _Xapian: https://xapian.org/
.. _Haystack: http://haystacksearch.org/
.. _Django-Woosh: https://github.com/JoeGermuska/django-whoosh/blob/master/django_whoosh/managers.py
