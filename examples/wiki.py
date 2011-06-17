# encoding: utf-8

from __future__ import unicode_literals

from marrow.norm.connection import Connection
from marrow.norm.document import Document
from marrow.norm.field import *



class Metadata(Document):
    __meta__ = dict(collection=None)
    
    tags = List(Text(transform=str.lower))


class WikiPage(Document):
    __meta__ = dict(collection='pages')
    
    title = Text('t', required=True)
    content = Text('c')
    # metadata = Metadata.embed()



if __name__ == '__main__':
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    conn = Connection("mongodb://localhost/test")
