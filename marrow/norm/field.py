# encoding: utf-8

from __future__ import unicode_literals


from marrow.util.object import NoDefault, CounterMeta



class Field(object):
    __metaclass__ = CounterMeta
    default = NoDefault
    
    def __init__(self, key=None, required=False, default=NoDefault, unique=False, primary=False, validator=None):
        self.key = key
        self.required = required
        self.default = default
        self.unique = unique
        self.primary = primary
        self.validator = validator
    
    def __repr__(self):
        return "%s()" % (self.__class__.__name__, )
    
    def __get__(self, obj, cls):
        if obj is None:
            return self
        
        try:
            return obj.__data__[self.key]
        
        except KeyError:
            pass
        
        if self.default is not NoDefault:
            if hasattr(self.default, '__call__'):
                return self.default(obj)
            
            return self.default
        
        if not self.required:
            return None
        
        raise AttributeError('Data for \'%s\' is missing.' % (self.key, ))
    
    def __set__(self, obj, value):
        if value is self.default:
            del obj.__data__[self.key]
            return
        
        obj.__data__[self.key] = value
    
    def __delete__(self, obj):
        del obj.__data__[self.key]


class Integer(Field):
    def __get__(self, obj, cls):
        return int(super(Integer, self).__get__(obj, cls))


class String(Field):
    pass


class Float(Field):
    pass


class List(Field):
    pass


class Embed(Field):
    pass


class IPAddress(Field):
    pass


class DateTime(Field):
    pass


