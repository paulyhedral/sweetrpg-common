# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
"""

class QueryOptions(object):
    """
    An object to store query options for a PyMongo find*() call.
    """

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
