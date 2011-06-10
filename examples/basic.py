# encoding: utf-8

from __future__ import unicode_literals

from marrow.norm.connection import Connection




if __name__ == '__main__':
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    conn = Connection("mongodb://localhost/test")
    