# encoding: utf-8

from __future__ import unicode_literals

import pymongo.errors

from marrow.util.text import normalize
from marrow.util.object import NoDefault, CounterMeta
from marrow.util.bunch import Bunch
from marrow.norm.connection import Connection
from marrow.norm.exception import OperationError
from marrow.norm.field import Field
from marrow.norm.registry import registry


log = __import__('logging').getLogger(__name__)


default_collection = lambda name: normalize(name) + 's'
default_identifier = lambda cls: cls.__module__ + ':' + cls.__name__


class Document(Field):
    """An attribute-access and dictionary-access object which can
    validate schema and pass values between MongoDB and Python.
    
    You can override a number of values (such as the collection name)
    by utilizing a __meta__ dictionary attribute.  This dict will be
    merged with its superclasses, if any.
    
    The schema is defined using Field instances as class attributes.
    
    Define an __id__ attribute to avoid potential migration issues
    in the future if using inheritance; doing so will utilize a
    registry of classes.  Not doing so stores the dot-colon notation
    path to the object, so if you refactor your code, lookup may fail!
    Note that none of this applies unless you are utilizing model
    inheritance.  (And even if you move a Document subclass to another
    module, if the name is unique it will still be found.)
    
    If using a Document schama purely for embedding, set the 
    __meta__.collection name to None.
    """
    
    __id__ = None
    
    class __metaclass__(CounterMeta):
        def __new__(meta, name, bases, attrs):
            fields = list()
            metadata = Bunch()
            flat = True
            root = list()
            
            for base in bases:
                if hasattr(base, '__fields__'):
                    fields.extend(base.__fields__)
                
                if hasattr(base, '__meta__'):
                    _ = dict(base.__meta__)
                    _['index'] = metadata.get('index', []) + _.get('index', [])
                    metadata.update(_)
                    
                    if base is not Document:
                        root.append(base)
                        flat = False
                    
                    else:
                        del metadata['collection']
                    
                    if not base.__meta__.inheritable:
                        metadata = Bunch()
                        root = list()
                        flat = True
            
            _ = dict(attrs.get('__meta__', {}))
            _['index'] = metadata.get('index', []) + _.get('index', [])
            metadata.update(_)
            
            collection = _.get('collection', None) or (root[-1].__collection__ if root else metadata.get('collection', default_collection))
            
            if callable(collection):
                collection = collection(name)
            
            attrs['__collection__'] = collection
            attrs['__meta__'] = metadata
            attrs['__flat__'] = flat
            
            for name_, value in sorted([(i, attrs[i]) for i in attrs if isinstance(attrs[i], Field)], cmp=lambda l,r: cmp(l[1]._counter, r[1]._counter)):
                if isinstance(value, Field):
                    if not value.key:
                        value.key = normalize(name_, fields)
                    
                    fields.append(name_)
            
            attrs['__fields__'] = fields
            
            result = CounterMeta.__new__(meta, name, bases, attrs)
            
            identifier = attrs.get('__id__', None) or default_identifier(result)
            
            if identifier != 'marrow.norm.document:Document':
                result.__meta__['identifier'] = identifier
                registry[name] = registry[identifier] = result
                
                if result.__collection__ and flat:
                    registry[result.__collection__] = result
            
            return result
    
    __meta__ = dict(
            collection = None,
            index = [], # list of tuples indicating indexes to create
            order = tuple(), # default sort order
            inheritable = True, # allow same-collection document inheritance
            capped = False, # False or a marrow.norm.tuples.CappedLimit instance
            safe = True, # are operations safe by default?
            pk = '_id', # primary key
        )
    
    def __init__(self, *args, **kw):
        self.__data__ = Bunch()
        
        if not args and not kw:
            return
        
        remaining = list(self.__fields__)
        consumed = list()
        
        for arg in args:
            name = remaining.pop(0)
            self[name] = arg
            consumed.append(name)
        
        for name in kw:
            if name in consumed:
                raise TypeError('%s got multiple values for keyword argument \'%s\'' % (self.__class__.__name__, name))
            
            setattr(self, name, kw.get(name))
        
        super(Document, self).__init__()
    
    @classmethod
    def embed(cls, *args, **kw):
        obj = cls()
        Field.__init__(obj, *args, **kw)
        return obj
    
    def __iter__(self):
        return iter(self.__data__)
    
    def __contains__(self, name):
        return name in self.__data__
    
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
    
    def __get__(self, obj, cls=None):
        if cls is None: return self
        
        return super(Document, self).__get__(obj, cls)
    
    def __set__(self, obj, value):
        return super(Document, self).__set__(obj, value)
    
    def __getitem__(self, name):
        return self.__data__[name]
    
    def __setitem__(self, name, value):
        self.__data__[name] = value
    
    def __delitem__(self, name):
        del self.__data__[name]
    
    def save(self, safe=NoDefault, insert=True, update=True, validate=True):
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
        
        if not insert and not update:
            raise ValueError("When saving you must allow inserts, updates, or both.")
        
        safe = self.__meta__.safe if safe is NoDefault else safe
        
        # if update and not self.dirty:
        #     log.debug("Attempted to save an unmodified document.")
        #     return
        
        collection = Connection().components().db[self.__collection__]
        
        try:
            if update:
                identifier = collection.save(self.__data__, safe=safe)
            
            else:
                identifier = collection.insert(self.__data__, safe=safe)
        
        except pymongo.errors.OperationFailure, e:
            log.exception("Unable to save document.")
            raise OperationError("Unable to save document.", e)
        
        setattr(self, self._meta.identifier, identifier)
    
