# encoding: utf-8

from __future__ import unicode_literals

import pymongo.errors

from marrow.util.text import normalize
from marrow.util.object import NoDefault
from marrow.util.bunch import Bunch
from marrow.norm.connection import Connection
from marrow.norm.exception import OperationError
from marrow.norm.field import Field


log = __import__('logging').getLogger(__name__)


class Document(object):
    """An attribute-access and dictionary-access object which can
    validate schema and pass values between MongoDB and Python.
    
    You can override a number of values (such as the collection name)
    by utilizing a __meta__ dictionary attribute.  This dict will be
    merged with its superclasses, if any.
    
    The schema is defined using Field instances as class attributes.
    """
    
    class __metaclass__(type):
        def __new__(meta, name, bases, attrs):
            fields = list()
            metadata = dict()
            path = list()
            
            for base in list(bases):
                if '__meta__' not in base.__dict__:
                    continue
                
                fields.extend(base.__dict__.get('__fields__', []))
                
                if not base.__meta__['inheritable']:
                    path = list()
                
                _ = dict(base.__dict__.get('__meta__', dict()))
                _['index'] = metadata.get('index', []) + _.get('index', [])
                
                if base is not Document:
                    path.append(base.__name__)
                
                metadata.update(_)
            
            path.append(name)
            metadata.update(attrs.get('__meta__', dict()))
            
            if callable(metadata.get('collection', None)):
                attrs['__collection__'] = metadata['collection'](path[0])
            
            else:
                attrs['__collection__'] = metadata['collection']
            
            metadata['path'] = '.'.join(path) # use real dot-colon notation here
            
            attrs['__meta__'] = Bunch(metadata)
            
            for name_, value in sorted([(i, attrs[i]) for i in attrs if isinstance(attrs[i], Field)], cmp=lambda l,r: cmp(l[1]._counter, r[1]._counter)):
                if isinstance(value, Field):
                    if not value.key:
                        value.key = normalize(name_, fields)
                    
                    fields.append(name_)
            
            attrs['__fields__'] = list(fields)
            
            return type.__new__(meta, name, bases, attrs)
    
    __meta__ = dict(
            collection = lambda name: normalize(name) + 's',
            index = [], # list of tuples indicating indexes to create
            order = tuple(), # default sort order
            inheritable = True, # allow same-collection document inheritance
            capped = False, # False or a marrow.norm.tuples.CappedLimit instance
            safe = True, # are operations safe by default?
            pk = '_id', # primary key
        )
    
    def __init__(self, *args, **kw):
        self.__data__ = dict(_cls=self.__meta__.path)
        
        remaining = list(self.__fields__)
        consumed = list()
        
        for arg in args:
            name = remaining.pop(0)
            self[name] = arg
            consumed.append(name)
        
        for name in kw:
            if name in consumed:
                raise TypeError('%s got multiple values for keyword argument \'%s\'' % (self.__class__.__name__, name))
            
            self[name] = kw.get(name)
    
    def __getitem__(self, name):
        if name not in self.__fields__:
            raise KeyError(name)
        
        return getattr(self, name)
    
    def __setitem__(self, name, value):
        if name not in self.__fields__:
            raise KeyError(name)
        
        setattr(self, name, value)
    
    def __iter__(self):
        return iter(self.__fields__)
    
    def __contains__(self, name):
        return name in self.__fields__
    
    def __len__(self):
        return len(self._data)
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
            ", ".join([("%s=%s" % (i, getattr(self, i))) for i in self.__fields__]))
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        if self.__meta__.collection != other.__meta__.collection:
            return False
        
        if self.__meta__.pk != other.__meta__.pk:
            return False
        
        return getattr(self, self.__meta__.pk) == getattr(other, other.__meta__.pk)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        identifier = getattr(self, self._meta.identifier, None)
        
        if identifier is None:
            return super(Document, self).__hash__()
        
        return hash(identifier)
    
    def save(self, safe=NoDefault, update=True, validate=True):
        """Save the current document; if it does not already exist,
        it will be created.
        
        If `safe` is True, then this operation will block pending the
        result from MongoDB.  If there is an error, an OperationError
        exception is raised.  Unsafe operations return immediately.
        
        If `update` is False, then only new inserts will be allowed.
        
        If `validate` is True, then the document will be compared to
        its schema and invalid data rejected, raising a ValidationError
        exception containing useful details of the failure.
        """
        
        if validate:
            self.validate()
        
        safe = self._meta.safe if safe is NoDefault else safe
        
        if update and not self.dirty:
            log.debug("Attempted to save an unmodified document.")
            return
        
        collection = Connection().components().db[self._meta.collection]
        
        try:
            if update:
                identifier = collection.save(self._document, safe=safe)
            
            else:
                identifier = collection.insert(self._document, safe=safe)
        
        except pymongo.errors.OperationFailure, e:
            log.exception("Unable to save document.")
            raise OperationError("Unable to save document.", e)
        
        setattr(self, self._meta.identifier, identifier)
        
        self.dirty = None
    
    def validate(self):
        """Validate the presence of required fields and ensure values
        are within expected ranges."""
        
        return True
