# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Query options for accessing MongoDB.
"""


class QueryOptions(object):
    """An object to store query options for a PyMongo find*() call."""

    # https://flask-rest-jsonapi.readthedocs.io/en/latest/filtering.html
    _filter_operators = {
        "eq": "$eq",
        "gt": "$gt",
        "ge": "$gte",
        "in_": "$in",
        "lt": "$lt",
        "le": "$lte",
        "ne": "$ne",
        "notin_": "$nin",
        # '': '$and',
        "isnot": "$not",
        # '': '$nor',
        # '': '$or',
        "is_": "$exists",
        # 'any': 'TODO',
        # 'between': 'TODO',
        # 'endswith': 'TODO',
        # 'has': 'TODO',
        # 'ilike': 'TODO',
        # 'like': 'TODO',
        # 'match': 'TODO',
        # 'notilike': 'TODO',
        # 'notlike': 'TODO',
        # 'startswith': 'TODO',
    }
    _sort_values = {
        "asc": 1,
        "dsc": -1,
    }

    def __init__(self, filters: dict = {}, projection: list = [], skip: int = 0, limit: int = 0, sort: list = []):
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

    def _process_filter(self, filter_info: dict):
        name = filter_info["name"]
        value = filter_info["val"]
        op = self._filter_operators.get(filter_info["op"], "$eq")
        return {name: {op: value}}

    def set_filters(self, filters: dict = None, from_querystring: list = None):
        """Sets filters for the query.

        :param dict filters: A dictionary of filters to set.
        :param list from_querystring: Filters to set in querystring format.
        """
        if filters is not None:
            self.filters = filters
        elif from_querystring is not None:
            filters = {}
            for f in from_querystring:
                filters.update(self._process_filter(f))
            self.filters = filters

    def set_projection(self, projection: list = None, from_querystring: list = None):
        """Sets projections for the query.

        :param list projection: A list of field names to include in the query results.
        :param list from_querystring: Projections to set in querystring format.
        """
        if projection is not None:
            self.projection = projection
        elif from_querystring is not None:
            self.projection = from_querystring

    def _process_sort(self, sort_item: dict):
        name = sort_item["field"]
        direction = self._sort_values.get(sort_item["order"], 1)
        return name, direction

    def set_sort(self, sort: list = None, from_querystring: list = None):
        """Sets sorting for the query results.

        :param list sort: A list of dictionaries containing field name and ordering.
        :param list from_querystring: Sorts to set in querystring format.
        """
        if sort is not None:
            self.sort = sort
        elif from_querystring is not None:
            self.sort = list(map(self._process_sort, from_querystring))
