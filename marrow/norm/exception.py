# encoding: utf-8

from __future__ import unicode_literals


class ConnectionError(Exception):
    """There was an unrecoverable error attempting to connect to MongoDB."""
    pass


