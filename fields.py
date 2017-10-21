from whoosh.fields import (
NUMERIC, IDLIST, COLUMN, DATETIME,
BOOLEAN, STORED, KEYWORD, ID, TEXT,
NGRAM, NGRAMWORDS
)

class IntegerField(NUMERIC):
    def __init__(self, stored=False, unique=False,
                 field_boost=1.0, shift_step=4, signed=True,
                 sortable=False, default=None):
        super().__init__(int, 32, stored, unique,
                 field_boost, 0, shift_step, signed,
                 sortable, default)
                 
class LongField(NUMERIC):
    def __init__(self, stored=False, unique=False,
                 field_boost=1.0, shift_step=4, signed=True,
                 sortable=False, default=None):
        super().__init__(long, 64, stored, unique,
                 field_boost, 0, shift_step, signed,
                 sortable, default)

class DecimalField(NUMERIC):
    '''
    Python Decimal type
    '''
    def __init__(self, decimal_places=32, stored=False, unique=False,
                 field_boost=1.0, shift_step=4, signed=True,
                 sortable=False, default=None):
        # first two parameters are irrelevant, only decimal_places
        #  works
        super().__init__(long, 64, stored, unique,
                 field_boost, decimal_places, shift_step, signed,
                 sortable, default)  
                 
class FloatField(NUMERIC):
    '''
    Floats are always 64 bit
    '''
    def __init__(self, stored=False, unique=False,
                 field_boost=1.0, shift_step=4, signed=True,
                 sortable=False, default=None):
        # bits irreleant, always 64
        super().__init__(float, 64, stored, unique,
                 field_boost, 0, shift_step, signed,
                 sortable, default)         

class NumericField(NUMERIC):
    '''
    bits must be 8, 16, 32, or 64, only works for int and long
    '''
    def __init__(self,  numtype=int, bits=32, stored=False, unique=False,
                 field_boost=1.0, decimal_places=0, shift_step=4, signed=True,
                 sortable=False, default=None):
        super().__init__(numtype, bits, stored, unique,
                 field_boost, decimal_places, shift_step, signed,
                 sortable, default)   

class IdListField(IDLIST):
    def __init__(self, stored=False, unique=False, expression=None,
                 field_boost=1.0):
        super().__init__(stored, unique, expression,
                 field_boost)
                 
class ColumnField(COLUMN):
    def __init__(self, columnobj=None):
        super().__init__(columnobj=None)
                      
class DateTimeField(DATETIME):
    def __init__(self, stored=False, unique=False, sortable=False):
        super().__init__(stored, unique, sortable)

class BooleanField(BOOLEAN):
    def __init__(self, stored=False, field_boost=1.0):
        super().__init__(stored, field_boost)

class StoredField(STORED):
    def __init__(self):
        pass
       
class KeywordField(KEYWORD):
    def __init__(self, stored=False, lowercase=False, commas=False,
                 scorable=False, unique=False, field_boost=1.0, sortable=False,
                 vector=None, analyzer=None):
        super().__init__(stored, lowercase, commas,
                 scorable, unique, field_boost, sortable,
                 vector, analyzer)
        
class IdField(ID):
    def __init__(self, stored=False, unique=False, field_boost=1.0,
                 sortable=False, analyzer=None):
        super().__init__(stored, unique, field_boost,
                 sortable, analyzer)

class TextField(TEXT):
    def __init__(self, analyzer=None, phrase=True, chars=False, stored=False,
                 field_boost=1.0, multitoken_query="default", spelling=False,
                 sortable=False, lang=None, vector=None,
                 spelling_prefix="spell_"):
        super().__init__(analyzer, phrase, chars, stored,
                 field_boost, multitoken_query, spelling,
                 sortable, lang, vector,
                 spelling_prefix)
                 
class NGamField(NGRAM):
    def __init__(self, minsize=2, maxsize=4, stored=False, field_boost=1.0,
                 queryor=False, phrase=False, sortable=False):
        super().__init__(minsize, maxsize, stored, field_boost,
                 queryor, phrase, sortable)

class NGamWordsField(NGRAMWORDS):
    def __init__(self, minsize=2, maxsize=4, stored=False, field_boost=1.0,
                 tokenizer=None, at=None, queryor=False, sortable=False):
        super().__init__(minsize, maxsize, stored, field_boost,
                 tokenizer, at, queryor, sortable)

