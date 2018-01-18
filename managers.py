import sys

#from whoosh import fields, index
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, SimpleParser
from datetime import datetime, timedelta
import time
from django.db import models
from django.forms.models import model_to_dict


#! auto-init with this data
class BaseManager:    
    def __init__(self):
        self._need_base = None
        self._need_index = None
        self._whoosh_schema = None
        self._schema_fields = None
        self.model = None
        self.pk_fieldname = None
        self.name = None
        
    def contribute_to_class(self, opts):
        self._need_base = opts.need_base
        self._need_index = opts.need_index
        self._whoosh_schema = opts.schema
        self._schema_fields = opts.schema_fields
        self.model = opts.model
        self.pk_fieldname = opts.pk_field.name
        #self.name = 



#! change schema?
#! file locked version
#! async version
#! fuzzy search
#! stem search
#! delete using fieldname
class Manager(BaseManager):
    '''
    A basic Whoosh manager.
    Every operation is self contained, and tidies after the action.
    Note that if multiple threads access the writing, any writing 
    operation can throw an error.
    '''
    def __init__(self):
        super().__init__()

    def bulk_add(self, it):
        start = time.time()
        ix = open_dir(self._need_base, self._need_index)
        end = time.time()
        print('opendir', 'took', str(end - start), 'time')
        start = time.time()
        writer = ix.writer()
        end = time.time()
        print('writer', 'took', str(end - start), 'time')
        for e in it:
            # expected inputs to dict with string values 
            if (issubclass(e.__class__, models.Model)):
                e = model_to_dict(e)
            data = {f : str(e[f]) for f in self._schema_fields}
            writer.add_document(e)
        writer.commit()      
        ix.close()

    def add(self, data):
        '''
        Write a document.
        Ignores keys not in schema. No data for unprovided schema keys.
        
        @param data object or dict of values. 
        '''
        # expected inputs to dict with string values 
        if (issubclass(data.__class__, models.Model)):
            data = model_to_dict(data)
        data = {f : str(data[f]) for f in self._schema_fields}
        
        start = time.time()
        ix = open_dir(self._need_base, self._need_index)
        end = time.time()
        print('opendir', ' took', str(end - start), 'time')
        start = time.time()
        writer = ix.writer()
        end = time.time()
        print('writer', ' took', str(end - start), 'time')
        writer.add_document(**data)
        start = time.time()
        writer.commit()
        end = time.time()
        print('commit', ' took', str(end - start), 'time')
        ix.close()

    def delete(self, key):
        '''
        Delete a document.
        
        @param key to match against pk field.
        '''
        # unusable on non-Model indexes
        # will throw error due to self.pk_fieldname?
        # assert/except?
        # expected inputs to dict with string values 
        key = str(key)
        ix = open_dir(self._need_base, self._need_index)
        writer = ix.writer()
        writer.delete_by_term(self.pk_fieldname, key, searcher=None)
        writer.commit() 
        ix.close() 
        
    def delete_when(self, fieldname, text):
        '''
        Delete documents.
        Match on any key.
        
        @param fieldname key to match against
        @param text match value. 
        '''
        ix = open_dir(self._need_base, self._need_index)
        writer = ix.writer()
        writer.delete_by_term(fieldname, text, searcher=None)
        writer.commit() 
        ix.close()

    def merge(self, data):
        '''
        Merge a document.
        Ignores keys not in schema. No data for unprovided schema keys.
        Checks for unique keys then matches against parameters.
        Slower than add(). Will create if entry does not exist.
        
        @param data object or dict of values.
        '''
        # "It is safe to use ``update_document`` in place of ``add_document``; if
        # there is no existing document to replace, it simply does an add."
        # expected inputs to dict with string values 
        if (issubclass(data.__class__, models.Model)):
            data = model_to_dict(data)
        data = {f : str(data[f]) for f in self._schema_fields}
        ix = open_dir(self._need_base, self._need_index)
        writer = ix.writer()
        writer.update_document(**data)
        writer.commit() 
        ix.close()


    def read(self, fieldnames, query, callback):
        start = time.time()
        ix = open_dir(self._need_base, self._need_index)
        end = time.time()
        print('opendir', ' took', str(end - start), 'time')
        r = None
        with ix.searcher() as searcher:
            start = time.time()
            #query = QueryParser(field, self._whoosh_schema).parse(query)
            query = SimpleParser(fieldnames, self._whoosh_schema).parse(query)
            end = time.time()
            print('query', ' took', str(end - start), 'time')
            callback(searcher.search(query))
        #ix.close()

    def size(self):
        ix = open_dir(self._need_base, self._need_index)
        r = ix.doc_count()
        ix.close()
        return r

        
class ManagerManager(Manager):
    def clear(self):
        '''
        Empty the index.
        '''
        self.ix.storage.clean()    

    def optimize(self):
        self.ix.optimize()
    
    def load(self):
        ix = open_dir(self._need_base, self._need_index)
        writer = ix.writer()
        for o in self.model.objects.all():
            data = dict([(fn, str(getattr(o, fn))) for fn in self._schema_fields])
            print(str(data))
            writer.add_document(**data)
        writer.commit()
        ix.close()
        
        
import threading

# Pointer to the module object instance, for module-wide storage.
# https://stackoverflow.com/questions/1977362/how-to-create-module-wide-variables-in-python#1978076
this = sys.modules[__name__]

this.blocking_lock = None
# map of path to file_desciptor (whoosh index)
this.ix_registry = {}

class RegistryInfo():
    def __init__(self, directory, lock):
        self.directory = directory
        self.lock = lock
        
def assert_index_registry(base, index):
    path = "{0}_{1}".format(base, index)
    if (path not in this.ix_registry):
            this.ix_registry[path] = RegistryInfo(open_dir(base, index), threading.Lock())
    return this.ix_registry[path]
    
    
    
class BlockingManagerManager(Manager):
    def contribute_to_class(self, opts):
        super().contribute_to_class(opts)
        #self.threadLock = threading.Lock()
        #self.ix = open_dir(self._need_base, self._need_index)
        info = assert_index_registry(self._need_base, self._need_index)
        self.ix = info.directory
        self.threadLock = info.lock
        
    def clear(self):
        '''
        Empty the index.
        '''
        self.threadLock.acquire()
        #On fileStorage and RAMStorage, clean()
        # Storage. Can only do on Filestorage.
        #ix.storage.destroy()
        self.ix.storage.clean()    
        self.threadLock.release()

    def optimize(self):
        self.threadLock.acquire()
        self.ix.optimize()
        self.threadLock.release()
        
        
                
class BlockingManager(Manager):
    '''
    A basic Whoosh manager.
    Every operation is self contained, and tidies after the action.
    The operations are blocking.
    '''
    def __init__(self):
        super().__init__()
        
    def contribute_to_class(self, opts):
        super().contribute_to_class(opts)
        self.threadLock = threading.Lock()
        self.ix = open_dir(self._need_base, self._need_index)
        
    def bulk_add(self, it):
        def to_dict(data):
            # expected inputs to dict with string values 
            if (issubclass(e.__class__, models.Model)):
                e = model_to_dict(e)
            return {f : str(e[f]) for f in self._schema_fields}
        it = [to_dict(data) for data in it]
        self.threadLock.acquire()
        writer = self.ix.writer()
        self.threadLock.release()
        for e in it:
            writer.add_document(e)
        writer.commit()      

    def add(self, data):
        '''
        Write a document.
        Ignores keys not in schema. No data for unprovided schema keys.
        
        @param data object or dict of values. 
        '''
        # expected inputs to dict with string values 
        if (issubclass(data.__class__, models.Model)):
            data = model_to_dict(data)
        data = {f : str(data[f]) for f in self._schema_fields}
        start = time.time()
        self.threadLock.acquire()
        end = time.time()
        print('aquire', ' took', str(end - start), 'time')
        writer = self.ix.writer()
        self.threadLock.release()
        writer.add_document(**data)
        writer.commit()
        
    def delete(self, key):
        '''
        Delete a document.
        
        @param key to match against pk field. 
        '''
        key = str(key)
        self.threadLock.acquire()
        writer = self.ix.writer()
        self.threadLock.release()
        writer.delete_by_term(self.pk_fieldname, key, searcher=None)
        writer.commit()

    def delete_when(self, fieldname, text):
        '''
        Delete documents.
        Match on any key.
        
        @param fieldname key to match against
        @param text match value. 
        '''
        self.threadLock.acquire()
        writer = self.ix.writer()
        self.threadLock.release()
        writer.delete_by_term(fieldname, text, searcher=None)
        writer.commit()
        
    def merge(self, **data):
        '''
        Merge a document.
        Ignores keys not in schema. No data for unprovided schema keys.
        Checks for unique keys then matches against parameters.
        Slower than add(). Will create if entry does not exist.
        
        @param data object or dict of values. 
        '''
        # expected inputs to dict with string values 
        if (issubclass(data.__class__, models.Model)):
            data = model_to_dict(data)
        data = {f : str(data[f]) for f in self._schema_fields}
        self.threadLock.acquire()
        writer = self.ix.writer()
        self.threadLock.release()
        writer.update_document(**data)
        writer.commit()

    def read(self, fieldnames, query, callback):
        r = None
        with self.ix.searcher() as searcher:
            start = time.time()
            query = SimpleParser(fieldnames, self._whoosh_schema).parse(query)
            end = time.time()
            print('query', ' took', str(end - start), 'time')
            callback(searcher.search(query))

    def size(self):
        r = self.ix.doc_count()
        return r
    
