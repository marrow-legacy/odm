# encoding: utf-8

from __future__ import unicode_literals


from marrow.util.object import NoDefault



class Field(object):
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
            return obj[self.key]
        
        except KeyError:
            pass
        
        if self.default is not NoDefault:
            if hasattr(self.default, '__call__'):
                value = self.default(obj)
                
                # Not sure if we really want to store the value...
                # Content-Length and Content-MD5 regeneration are useful!
                # if self.rw:
                #     obj[self.header] = value
                
                return value
            
            return self.default
        
        raise AttributeError('WSGI environment does not contain %s key.' % (self.header, ))
    
    def __set__(self, obj, value):
        if not self.rw or obj.final:
            raise AttributeError('%s is a read-only value.' % (self.header, ))
        
        if value is None:
            del obj[self.header]
            return
        
        obj[self.header] = value
    
    def __delete__(self, obj):
        if not self.rw or obj.final:
            raise AttributeError('%s is a read-only value.' % (self.header, ))
        
        del obj[self.header]


class Integer(Field):
    def __get__(self, obj, cls):
        try:
            return int(super(Int, self).__get__(obj, cls))
        except AttributeError:
            return None
        except TypeError:
            return None
    
    def __set__(self, obj, value):
        super(Int, self).__set__(obj, binary(value))


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


