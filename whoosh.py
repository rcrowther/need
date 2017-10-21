import os
#from django.db.models import signals
from django.conf import settings
from django.db import models
from django.apps import apps
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldError, ImproperlyConfigured
)

from whoosh import fields #, index
from whoosh.index import create_in, exists_in
from whoosh.fields import FieldType

from .managers import BaseManager, Manager, BlockingManager
from .fields import TextField, IdField
#from .models import File

# need the add/update triggers in there
# and first-time build
# options to be checked and go through
# and delete index what we have command.
# stemming
# absolute URL option
# autofield automatic inclusion if present?
      
#! make as a dict
def default_woosh_field(klass):
    '''
    Given a Model Field, return a guess for a Whoosh field.
    A rough-guess at likely sense, not a definition of what
    can be done.
    '''
    if (klass == models.AutoField): 
        return IdField(unique=True)
    if (klass == models.CharField):
        return TextField(stored=True)
    if (
        klass == models.DateTimeField
        ):
        return DateTimeField(stored=False)
    if ( 
        klass == models.DateField
        or klass == models.UUIDField
        ):
        return IdField
    if (
        klass == models.EmailField
        or klass == models.URLField
        ):
        return IdField(stored=True)
    return None


class DeclarativeFieldsMetaclass(type):
    """collect Whoosh fields declared on classes."""
    def __new__(mcs, name, bases, attrs):
        # collect fields from current class.
        current_fields = {}
        for k, v in list(attrs.items()):
            if isinstance(v, FieldType):
                current_fields[k] = v
                attrs.pop(k)

        new_class = super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        base_fields = {}
        for base in new_class.__mro__:
            # Collect fields from base class.
            if hasattr(base, 'whoosh_fields'):
                base_fields.update(base.whoosh_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in base_fields:
                    base_fields.pop(attr)
                    
        if (not hasattr(new_class, 'whoosh_fields')):
            new_class.whoosh_fields = {}
        new_class.whoosh_fields.update(base_fields)
        new_class.whoosh_fields.update(current_fields)
        return new_class
        
        

class WooshOptions:
    def __init__(self, app_label, module, class_name, options=None):
        self.whoosh_index = getattr(options, 'whoosh_index', None)
        if not self.whoosh_index:
            self.whoosh_index = "{0}_{1}".format(app_label, class_name)  
        self.whoosh_base = getattr(options, 'whoosh_base') 
        self.module = module
        self.class_name = class_name
        self.requested_fields = getattr(options, 'fields')
        self.declared_fields = getattr(options, 'declared_fields')
        self.model = getattr(options, 'model', None)
        if (self.model):
            self.model_fieldmap = {field.name : field.__class__ for field in self.model._meta.fields}
            self.pk_field = self.model._meta.pk
        else:
            self.model_fieldmap = None
            self.pk_field = None
        self.schema_fields = []
        self.schema = None

    def __str__(self):
        return "WooshOptions(whoosh_index:{0}, whoosh_base:{1}, module:{2}, model:{3}, requested_fields:{4}, declared_fields:{5}, schema_fields:{6})".format(
        self.whoosh_index,
        self.whoosh_base,
        self.module,
        self.model,
        self.requested_fields,
        self.declared_fields,
        self.schema_fields
        )


class WhooshMetaclass(DeclarativeFieldsMetaclass):
    def _validate_raw_opts(mcs, module, class_name, opts):
        if not settings.WHOOSH:
            raise TypeError("Whoosh class  {0}.{1} must have an available setting 'WHOOSH' to define the base folder.".format(
                module,
                class_name
                )
            )
        requested_fields = getattr(opts, 'fields', None)
        if requested_fields is None:
                raise ImproperlyConfigured(
                    "Whoosh class {0}.{1} doesn't declare a 'fields' attribute.".format(
                    module, 
                    class_name
                    )
                )
       
        # We check if a string was passed to `fields`,
        # which is likely to be a mistake where the user typed ('foo') instead
        # of ('foo',)
        if isinstance(requested_fields, str):
            raise TypeError("Whoosh class {0}.{1}s.Meta.fields cannot be a string. Did you mean to type: ('{2}s',)?".format(
                module,
                class_name,
                requested_fields,
                )
            )

    def _validate_clean_opts(mcs, opts):
        '''stub for model validation'''
        pass
        
    def _schema_fields(mcs, opts):
        b = {}
        for fieldname in opts.requested_fields:
            declared = opts.declared_fields.get(fieldname)
            if (declared):
                b[fieldname] = declared
            else:
                raise ImproperlyConfigured(
                    "Whoosh class {0}.{1} requested field {2} not declared.".format(
                        opts.module, 
                        opts.class_name,
                        fieldname
                        )
                    )
        return b
        
    def _first_run(mcs, whoosh_index, whoosh_schema):
        if not exists_in(settings.WHOOSH, whoosh_index):
            create_in(settings.WHOOSH, whoosh_schema, whoosh_index)


    def __new__(mcs, name, bases, attrs):
        #print('new WhooshMetaclass : ' + name)
        super_new = super().__new__

        # This metaclass will run on a base model such as Whoosh or 
        # ModelWhoosh. We want to check for required attributes and
        # build meta info, but not on bases themselves.
        parents = [b for b in bases if isinstance(b, WhooshMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        module = attrs.pop('__module__')

        # get opts (from Meta). Fail if none
        opts = attrs.pop('Meta', None)
        if not opts:
            raise ImproperlyConfigured(
                "Whoosh class {0}.{1} must have a 'meta' attribute.".format(module, name)
            )
       
        # make the new class
        new_class = super_new(mcs, name, bases, attrs)  

        # load the fields to the options (now we have them)
        opts.declared_fields = new_class.whoosh_fields
                    
        #print('meta meta:' + str(attrs))

        #get the base details for the whoosh index path
        whoosh_index = getattr(opts, 'whoosh_index', None)
        app_label = getattr(opts, 'app_label', None)
        if ((whoosh_index is None) and (app_label is None)):
            app_config = apps.get_containing_app_config(module)
            if app_config is None:
                raise ImproperlyConfigured(
                    "Whoosh class {0}.{1} doesn't declare an explicit whoosh_index or app_label and isn't in an application in INSTALLED_APPS.".format(module, name)
                )
            else:
                app_label = app_config.label
        new_class._validate_raw_opts(module, name, opts)
        opts.whoosh_base = settings.WHOOSH
        
        # make the meta options class, filtering unwanted info
        clean_opts = new_class._meta = WooshOptions(app_label, module, name, opts) 
        
        # catch a few errors, for good reports
        new_class._validate_clean_opts(clean_opts)
        
        # build scema info, populate meta
        schema_fields = new_class._meta.schema_fields = new_class._schema_fields(clean_opts)
        whoosh_schema = new_class._meta.schema = fields.Schema(**schema_fields)
        #print('new_class._meta:' + str(new_class._meta))

        # if needed, create index folders
        new_class._first_run(new_class._meta.whoosh_index, whoosh_schema) 
        
        # set managers
        managers = {k:v for k,v in attrs.items() if isinstance(v, BaseManager)}
        if (not managers):
            if 'actions' in attrs:
                raise ImproperlyConfigured(
                    "No manager on Whoosh class {0}.{1}, but an 'actions' attribute blocks auto-create.".format(
                    module, 
                    name
                    )
                ) 
        if (not 'actions' in managers):
            new_class.actions = Manager()
            managers['actions'] = new_class.actions
        for manager in managers.values():
            manager.contribute_to_class(clean_opts)
            

        return new_class

        
        
class Whoosh(metaclass=WhooshMetaclass):
    pass



class ModelWhooshMetaclass(WhooshMetaclass):
    def _validate_clean_opts(mcs, opts):
        model = getattr(opts, 'model', None)
        if model is None:
                raise ImproperlyConfigured(
                    "ModelWhoosh class {0}.{1} must declare a 'model' attribute.".format(
                    opts.module, 
                    opts.class_name
                    )
                )        
        model_fieldnames = list(opts.model_fieldmap.keys())
        for fieldname in opts.requested_fields:
            if fieldname not in model_fieldnames:
                raise ImproperlyConfigured(
                    "ModelWhoosh class {0}.{1} requests a field '{2}' not in Model {3}.".format(
                    opts.module, 
                    opts.class_name, 
                    fieldname,
                    opts.model.__name__
                    )
                )              

    def _schema_fields(mcs, opts):        
        # add the pk field if missing
        fields_to_use = set(opts.requested_fields)
        fields_to_use.add(opts.pk_field.name)
        b = {}
        for fieldname in fields_to_use:
            declared = opts.declared_fields.get(fieldname)
            if (declared):
                b[fieldname] = declared
            else:
                ## can it be defaulted?
                defaulted = default_woosh_field(opts.model_fieldmap[fieldname])
                if defaulted:
                    b[fieldname] = defaulted
                else:
                    #? special note for pk fields?
                    raise ImproperlyConfigured(
                        "Whoosh class {0}.{1} requested field '{2}' not declared and can not be defaulted.".format(
                        opts.module,
                        opts.class_name, 
                        fieldname
                        )
                    )
            # pk should always be 'stored'
            if (fieldname == opts.pk_field.name):
                b[fieldname].stored = True
        return b
        
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        return new_class
        
        
class ModelWhoosh(metaclass=ModelWhooshMetaclass):
    pass




        ##get_absolute_url_override = settings.ABSOLUTE_URL_OVERRIDES.get(opts.label_lower)
        ##if get_absolute_url_override:
        ##    setattr(cls, 'get_absolute_url', get_absolute_url_override)


# not exists
#signals.post_syncdb.connect(create_index)
#  django.db.models.signals.pre_migrate¶



#def update_index(sender, instance, created, **kwargs):
    ##storage = filestore.FileStorage(settings.WHOOSH_INDEX)
    ##ix = index.Index(storage, schema=WHOOSH_SCHEMA)
    #ix = open_dir(settings.WHOOSH_INDEX)
    #writer = ix.writer()
    #if created:
        #writer.add_document(title=instance.title, content=instance.body,
                                    #url=instance.get_absolute_url())
        #writer.commit()
    #else:
        #writer.update_document(title=instance.title, content=instance.body,
                                    #url=instance.get_absolute_url())
        #writer.commit()

#def index_add():
    #ix = open_dir(settings.WHOOSH_INDEX)
    #writer = ix.writer()
    #writer.add_document(title='Saxon-English man loses at tombola', content='A Whitworth man who bought a ticket for a tombola failed to win a prize',
                                 #url='filemanager/file/9')
    ###writer.add_document(title='Brexit Politics', content='Policies criticised after national scandal',
      ##                            url='filemanager/file/2')
    #writer.commit()
    #print('added?')
#signals.post_save.connect(update_index, sender=File)
