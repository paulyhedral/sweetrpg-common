# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Test cases for QueryOptions
"""

from sweetrpg_db.mongodb.options import QueryOptions


def test_options_init():
    filters = {}
    projection = []
    skip = 0
    limit = 1
    sort = []
    o = QueryOptions(filters, projection, skip, limit, sort)
    assert o is not None
    assert o.filters == filters
    assert o.projection == projection
    assert o.skip == skip
    assert o.limit == limit
    assert o.sort == sort


def test_options_set_by_type():
    filters = {"field": {"op": "value"}}
    projection = ["field"]
    skip = 0
    limit = 1
    sort = [{"field": -1}]
    o = QueryOptions()
    o.set_filters(filters=filters)
    o.set_projection(projection=projection)
    o.skip = skip
    o.limit = limit
    o.set_sort(sort=sort)
    assert o is not None
    assert o.filters == filters
    assert o.projection == projection
    assert o.skip == skip
    assert o.limit == limit
    assert o.sort == sort


def test_options_set_by_querystring():
    filters = [{"name": "field", "op": "eq", "val": "v"}]
    projection = ["field"]
    sort = [{"field": "field", "order": 1}]
    o = QueryOptions()
    o.set_filters(from_querystring=filters)
    o.set_projection(from_querystring=projection)
    o.set_sort(from_querystring=sort)
    assert o is not None
    # TODO: more assertions
    # assert o.filters == {"field": {"op": "value"}}
    # assert o.projection == projection
    # assert o.sort == [{"field": 1}]
