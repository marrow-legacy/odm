# encoding: utf-8

from __future__ import unicode_literals

from marrow.util.tuple import NamedTuple


class ConnectionInstance(NamedTuple):
    _fields = ('connection', 'db')


class CappedLimit(NamedTuple):
    _fields = ('size', 'count')
