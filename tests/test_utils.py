# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
"""

from sweetrpg_common.db.mongodb.utils import to_datetime


def test_to_datetime():
    x = to_datetime(0)
