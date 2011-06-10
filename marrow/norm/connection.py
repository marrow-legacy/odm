# encoding: utf-8

from __future__ import unicode_literals

import multiprocessing
import threading

from marrow.util.convert import array, boolean
from marrow.util.url import URL
from marrow.norm.exception import ConnectionError
from marrow.norm.tuples import ConnectionInstance

from pymongo import Connection as PyMongoConnection


__all__ = ['Connection']



class Connection(object):
    """A connection pool for MongoDB."""
    
    log = __import__('logging').getLogger(__name__)
    
    def __new__(cls, url=None):
        """Singleton pattern implementation."""
        
        if url is None and '__shared' not in cls.__dict__:
            raise ConnectionError("An existing shared connection pool is not available.")
        
        if not '__shared' in cls.__dict__:
            cls.__shared = object.__new__(cls, url)
        
        return cls.__shared
    
    def __init__(self, url):
        """Initialize a connection pool to a specific MongoDB server or cluster, and database."""
        
        self.url = URL(url, port="27017") if not isinstance(url, URL) else url
        self.pool = dict()
        
        self.log.info("Marrow NORM connecting to: %s", self.url)
        
        self.components()
    
    def components(self, reconnect=False):
        url = self.url
        pool = self.pool
        identity = self.identity()
        
        if identity not in pool or reconnect:
            try:
                parts = dict(
                        host = array(url.host) if ',' in url.host else url.host,
                        port = int(url.port),
                        max_pool_size = int(url.query.get('max_pool_size', 10)),
                        slave_okay = boolean(url.query.get('slave_okay', False)),
                        network_timeout = int(url.query.get('network_timeout', 0)) or None,
                        document_class = dict, # todo
                        tz_aware = boolean(url.query.get('tz_aware', True))
                    )
                
                connection = PyMongoConnection(**parts)
                db = connection[unicode(url.path[1:] or 'test')]
                
                if url.user and url.password:
                    db.authenticate(url.user, url.password)
                
                pool[identity] = ConnectionInstance(connection, db)
            
            except Exception, e:
                raise ConnectionError("Could not connect to MongoDB.", e)
        
        return pool[identity]
    
    @staticmethod
    def identity():
        identity = multiprocessing.current_process()._identity
        
        return (0 if not identity else identity[0],
            threading.current_thread().ident)
