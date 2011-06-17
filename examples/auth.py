# encoding: utf-8

from __future__ import unicode_literals

import string
import scrypt

from datetime import datetime
from random import choice

from marrow.norm.connection import Connection
from marrow.norm.document import Document
from marrow.norm.field import *



class Credential(Document):
    def validate(self):
        raise NotImplementedError


class PasswordCredential(Credential):
    __password = Text(key='p')
    difficulty = Float(key='d', default=0.5) # seconds
    
    @property
    def password(self):
        return None
    
    @password.setter
    def password(self, value):
        salt = b''.join([choice(Text.printable) for i in range(64)])
        self.__password = scrypt.encrypt(salt, value, maxtime=self.difficulty)
    
    @password.deleter
    def password(self):
        self.__password = None
    
    def validate(self, password):
        try:
            scrypt.decrypt(self.__password, password, self.difficulty)
        
        except scrypt.error:
            return False
        
        return True


class FailedLogin(Document):
    __meta__ = dict(collection=None)
    
    location = IPAddress(key='ip')
    when = DateTime(key='ts', default=lambda: datetime.utcnow())


class User(Document):
    identity = Text(required=True)
    credentials = List(Credential)
    
    created = DateTime()
    modified = DateTime()
    
    last = DateTime()
    failed = List(FailedLogin)


if __name__ == '__main__':
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    conn = Connection("mongodb://localhost/test")
