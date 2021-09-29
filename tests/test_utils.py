# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from sweetrpg_db.utils import to_datetime, to_timestamp
from bson.timestamp import Timestamp
from datetime import datetime
import time


def test_none_to_datetime():
    v = to_datetime(None)
    assert v is None


def test_timestamp_to_datetime():
    t = Timestamp(3, 200)
    v = to_datetime(t)
    assert isinstance(v, datetime)


def test_datetime_to_datetime():
    now = datetime.now()
    v = to_datetime(now)
    assert isinstance(v, datetime)
    assert v == now


def test_str_to_datetime():
    s = "1011-12-13T01:02:03.004"
    v = to_datetime(s)
    assert isinstance(v, datetime)
    assert v.year == 1011
    assert v.month == 12
    assert v.day == 13
    assert v.hour == 1
    assert v.minute == 2
    assert v.second == 3
    assert v.microsecond == 4000


def test_dict_to_datetime():
    now = 28800000
    s = {"$date": now}
    v = to_datetime(s)
    assert isinstance(v, datetime)


def test_float_to_datetime():
    t = time.time()
    v = to_datetime(t)
    assert isinstance(v, datetime)


def test_none_to_timestamp():
    v = to_timestamp(None)
    assert v is None


def test_datetime_to_timestamp():
    d = datetime.utcnow()
    v = to_timestamp(d)
    assert isinstance(v, Timestamp)


def test_int_to_timestamp():
    i = 1348129348
    v = to_timestamp(i)
    assert isinstance(v, Timestamp)
    assert v.time == i
    assert v.inc == 0
