# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
"""

class QueryOptions(object):
    """
    An object to store query options for a PyMongo find*() call.
    """

    _filter_operators = {
        'eq': '$eq',
        'gt': '$gt',
        'ge': '$gte',
        'in_': '$in',
        'lt': '$lt',
        'le': '$lte',
        'ne': '$ne',
        'notin_': '$nin',
        # '': '$and',
        'isnot': '$not',
        # '': '$nor',
        # '': '$or',
        'is_': '$exists',
    }
    _sort_values = {
        'asc': 1,
        'dsc': -1,
    }

    def __init__(self, filters:dict=None, projection:list=None, skip:int=0, limit:int=0, sort:list=None):
        """Initialize the QueryOptions object.
        :param dict filters: A dictionary of filters to apply to the query.
        :param list projection: A list of attribute names to include in the returned result. If `None`, all attributes are returned.
        :param int skip: An offset to use for pagination.
        :param int limit: The maximum number of results to return.
        :param list sort: A list of key-value pairs specifying the attributes to sort on.
        """
        self.filters = filters
        self.projection = projection
        self.skip = skip
        self.limit = limit
        self.sort = sort

    def __repr__(self):
        return f"<QueryOptions(filters={self.filters}, projection={self.projection}, skip={self.skip}, limit={self.limit}, sort={self.sort})>"

    def _process_filter(filter:dict):
        name = filter['name']
        value = filter['val']
        op = _filter_operators.get(filter['op'], '$eq')
        return { name: { op: value } }

    def set_filters(self, filters:dict=None, from_querystring:list=None):
        if filters is not None:
            self.filters = filters
        elif from_querystring is not None:
            self.filters = map(self._process_filter, filters)

    def set_projection(self, projection=None, from_querystring:list=None):
        if projection is not None:
            self.projection = projection
        elif from_querystring is not None:
            self.projection = from_querystring

    def _process_sort(sort_item:dict):
        name = sort_item['field']
        direction = _sort_values.get(sort_item['order'], 1)
        return { name: direction }

    def set_sort(self, sort:list=None, from_querystring:list=None):
        if sort is not None:
            self.sort = sort
        elif from_querystring is not None:
            self.sort = map(self._process_sort, from_querystring)
