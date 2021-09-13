# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from datetime import datetime
from bson.timestamp import Timestamp
import logging


def to_datetime(value, attr=None, data=None, **kwargs):
    """Deserialize database value to Python datetime.
    :param any value:
    :param str attr:
    :param object data:
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
        value = datetime.strptime(value)
    logging.debug("value (converted?): %s", value)
    return datetime.fromtimestamp(float(value))

def to_timestamp(value, attr=None, obj=None, **kwargs):
    """Serialize object value to MongoDB timestamp.
    :param any value:
    :param str attr: The name of the attribute being serialized.
    :param object obj:
    :param dict kwargs:
    :return bson.timestamp.Timestamp: MongoDB Timestamp object
    """
    logging.debug("to_timestamp: value (parameter): %s", value)
    if value is None:
        logging.debug("to_timestamp: None")
        return None
    return Timestamp(value.timestamp(), 0)
