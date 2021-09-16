# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow import Schema, fields, EXCLUDE
from marshmallow import pre_load
from datetime import datetime


class BaseDBSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def handle_id(self, in_data, **kwargs):
        in_data["id"] = in_data.get("_id") or in_data.get("id")
        return in_data

    @pre_load
    def handle_dates(self, in_data, **kwargs):
        for k in ["created_at", "updated_at", "deleted_at"]:
            if isinstance(in_data.get(k), datetime):
                in_data[k] = in_data[k].isoformat()
        return in_data

    id = fields.Str()  # as_string=True, dump_only=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    deleted_at = fields.DateTime(allow_none=True)
