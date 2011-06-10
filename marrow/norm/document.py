# encoding: utf-8

from __future__ import unicode_literals

import pymongo.errors

from marrow.util.object import NoDefault
from marrow.norm.connection import Connection
from marrow.norm.exception import OperationError


log = __import__('logging').getLogger(__name__)


class Document(object):
    """An attribute-access and dictionary-access object which can
    validate schema and pass values between MongoDB and Python.
    
    You can override a number of values (such as the collection name)
    by utilizing a __meta__ dictionary attribute.  This dict will be
    merged with its superclasses, if any.
    
    The schema is defined using Field instances as class attributes.
    """
    
    __meta__ = dict(
            collection = lambda cls: cls.__name__.lower(),
            index = [], # list of tuples indicating indexes to create
            order = tuple(), # default sort order
            inheritable = True, # allow same-collection document inheritance
            capped = False, # False or a marrow.norm.tuples.CappedLimit instance
            safe = True, # are operations safe by default?
        )
    
    def __init__(self, **kw):
        pass
    
    def __getitem__(self, name):
        if name not in self._meta.field.names:
            raise KeyError(name)
        
        return getattr(self, name)
    
    def __setitem__(self, name, value):
        if name not in self._meta.field.names:
            raise KeyError(name)
        
        setattr(self, name, value)
    
    def __iter__(self):
        return iter(self._meta.field.names)
    
    def __contains__(self, name):
        return name in self._meta.field.names
    
    def __len__(self):
        return len(self._data)
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
            ", ".join([("%s=%s" % (i, getattr(self, i))) for i in self._meta.field.names]))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return getattr(self, self._meta.identifier) == getattr(other, other._meta.identifier)
        
        return False
    
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
