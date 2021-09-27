# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Test cases for BaseSchema
"""

from sweetrpg_db.schema.base import BaseSchema
from marshmallow import fields
from datetime import datetime


def test_base_schema():
    class TestSchema(BaseSchema):
        name = fields.Str()

    data = {"id": "1", "name": "Test", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    schema = TestSchema()
    obj = schema.from_dict(data)
    assert obj is not None
    assert obj.id == "1"
    assert obj.name == "Test"
    assert isinstance(obj.created_at, datetime)
    assert isinstance(obj.updated_at, datetime)
