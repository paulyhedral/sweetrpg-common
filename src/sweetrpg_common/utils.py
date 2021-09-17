# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Utilities.
"""

from datetime import datetime
from bson.timestamp import Timestamp
import logging


def to_datetime(value, attr=None, data=None, **kwargs):
    """Deserializes a database value to a Python datetime.
    This function can be used as a callback for the Marshmallow :class:`fields.Function`
    field type.

    :param any value: The source value to convert to a Python datetime object. This can
        be a MongoDB :class:`bson.timestamp.Timestamp`, an ISO-formatted date/time
        string, or a UTC unix timestamp value.
    :param str attr: The name of the attribute being deserialized.
    :param object data: The object associated.
    :param dict kwargs:
    :return datetime.datetime: Python datetime object
    """
    logging.debug("to_datetime: value (parameter): %s", value)

    if value is None:
        logging.debug("to_datetime: None")
        return None
    elif isinstance(value, Timestamp):
        logging.debug("to_datetime: Timestamp")
        value = value.as_datetime().timestamp()
    elif isinstance(value, datetime):
        logging.debug("to_datetime: datetime")
        return value
    elif isinstance(value, str):
        logging.debug("to_datetime: str")
        value = datetime.fromisoformat(value)
        return value

    logging.debug("value (converted?): %s", value)
    return datetime.fromtimestamp(float(value))


def to_timestamp(value, attr=None, obj=None, **kwargs):
    """Serialize an object value to a MongoDB timestamp.
    This function can be used as a callback for the Marshmallow :class:`fields.Function`
    field type.

    :param any value: The source value to convert to a MongoDB :class:`bson.timestamp.Timestamp`. This
                      can be a `datetime` object, or a time/increment tuple.
    :param str attr: The name of the attribute being serialized.
    :param object obj:
    :param dict kwargs:
    :return bson.timestamp.Timestamp: MongoDB Timestamp object
    """
    logging.debug("to_timestamp: value (parameter): %s", value)

    if value is None:
        logging.debug("to_timestamp: None")
        return None
    if isinstance(value, datetime):
        logging.debug("to_timestamp: datetime")
        return Timestamp(value, 0)

    logging.debug("value (converted?): %s", value)
    return Timestamp(int(value), 0)
