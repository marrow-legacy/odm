# encoding: utf-8

from __future__ import unicode_literals


from marrow.util.object import NoDefault, CounterMeta
from marrow.norm.exception import ValidationError



class Field(object):
    __metaclass__ = CounterMeta
    _default = NoDefault
    _value = NoDefault
    
    def __init__(self, key=None, required=False, default=NoDefault, unique=False, primary=False, transform=None, validator=None):
        self._key = key
        self._required = required
        self._default = default
        self._unique = unique
        self._primary = primary
        self._transform = transform
        self._validator = validator
    
    def __repr__(self):
        return "%s()" % (self.__class__.__name__, )
    
    def __get__(self, obj, cls=None):
        if obj is None: return self
        
        result = obj[self._key]
        
        if result is NoDefault and self.default is not NoDefault:
            if callable(self.default):
                return self.default(obj)
            
            return self.default
        
        if not self.required:
            return None
        
        raise AttributeError('Data for \'%s\' is missing.' % (self.key, ))
    
    def __set__(self, obj, value):
        if value is self.default:
            del obj[self._key]
            return
        
        if self.required and value in (None, NoDefault):
            raise ValidationError()
        
        if self.validator and not self.validator(value):
            raise ValidationError()
        
        obj[self._key] = value
    
    def __delete__(self, obj):
        if self.required:
            raise ValidationError()
        
        del obj[self._key]


class Integer(Field):
    def __get__(self, obj, cls=None):
        if obj is None: return self
        return int(super(Integer, self).__get__(obj, cls))
    
    def __set__(self, obj, value):
        return super(Integer, self).__set__(obj, int(value))


class Boolean(Field):
    pass


class Text(Field):
    def __get__(self, obj, cls=None):
        if obj is None: return self
        return unicode(super(Text, self).__get__(obj, cls), 'utf-8')
    
    def __set__(self, obj, value):
        return super(Text, self).__set__(obj, unicode(value, 'iso8859-1').encode('utf-8'))


class Float(Field):
    def __get__(self, obj, cls=None):
        if obj is None: return self
        return float(super(Float, self).__get__(obj, cls))
    
    def __set__(self, obj, value):
        return super(Float, self).__set__(obj, float(value))


class Decimal(Field):
    pass


class List(Field):
    def __init__(self, kind, *args, **kw):
        self.kind = kind
        super(List, self).__init__(*args, **kw)


class Embed(Field):
    pass


class IPAddress(Field):
    pass


class Date(Field):
    pass


class Time(Field):
    pass


class TimeDelta(Field):
    pass



class DateTime(Field):
    pass


class DomainField(Field):
    pass


class URLField(DomainField):
    pass


class EMailAddress(DomainField):
    pass


class Dictionary(Field):
    pass


class Set(Field):
    pass


class Binary(Field):
    pass


class ObjectID(Field):
    pass


class Association(Field):
    """Like reference, but generic."""
    pass


class Reference(Association):
    """Specific to a given Document model."""
    pass


class File(Field):
    pass


class Point(Field):
    pass


class Slug(Field):
    """Make use of marrow.util's normalize method."""
    pass


class Query(Field):
    """Implements one:many relationship."""
    pass
