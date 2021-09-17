# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
"""

from ..exceptions import ObjectNotFound
from bson.objectid import ObjectId
from bson.timestamp import Timestamp
import datetime
from .options import QueryOptions
from pymongo.write_concern import WriteConcern
import logging


class MongoDataRepository(object):
    """
    A repository class for interacting with a MongoDB database.
    """

    def __init__(self, **kwargs):
        """Create a MongoDB repository instance.

        :param kwargs: Keyword arguments for setting up the repository connection.
        :key class model: The class of the model for this connection.
        :key class schema: The class of the schema used for deserializing objects from the database.
        :key str id_attr: (Optional) The name of the ID attribute for records in the database.
        :key PyMongo mongo: A :class:`PyMongo` object used for connecting to the database.
        """
        self.model_class = kwargs["model"]
        self.schema_class = kwargs["schema"]
        self.id_attr = kwargs.get("id_attr") or "_id"
        self.mongo = kwargs.get("mongo")
        self.collection = getattr(self.model_class, "__tablename__")

    def __repr__(self):
        return f"""\
        <MongoDataRepository(model_class={self.model_class},
                             schema_class={self.schema_class},
                             id_attr={self.id_attr},
                             collection={self.collection})>
        """

    def _handle_value(self, value):
        """ """
        if isinstance(value, ObjectId):
            logging.debug("converting ObjectId('%s')...", value)
            return str(value)
        elif isinstance(value, datetime.datetime):
            logging.debug("converting datetime value '%s'...", value)
            d = value.replace(tzinfo=datetime.timezone.utc)
            return d.isoformat(timespec="milliseconds")
        elif isinstance(value, Timestamp):
            logging.debug("converting Timestamp '%s'...", value)
            return value.as_datetime()
        elif isinstance(value, list):
            logging.debug("converting list '%s'...", value)
            return list(map(lambda v: self._handle_value(v), value))

        logging.debug("returning unprocessed value '%s'...", value)
        return value

    def _modify_record(self, record: dict) -> dict:
        """ """
        modified_record = {}
        for k, v in record.items():
            logging.debug("k: %s, v: %s", k, v)
            if k == "_id":
                k = "id"
            modified_value = self._handle_value(v)
            modified_record[k] = modified_value
            logging.debug("k: %s, v (modified): %s", k, modified_value)

        return modified_record

    def create(self, data: dict):
        """Inserts a new object in the database with the data provided.

        :param dict data: The data for the object
        :return ObjectId: The ID of the object inserted, or `None`
        """
        logging.debug("data: %s", data)
        collection_name = self.collection
        logging.debug("collection_name: %s", collection_name)
        collection = self.mongo.db[collection_name]
        logging.debug("collection: %s", collection)
        result = collection.with_options(write_concern=WriteConcern(w=3, j=True)).insert_one(data)
        logging.debug("result: %s", result)
        if result is None:
            return None
        record_id = result.inserted_id
        logging.debug("record_id: %s", record_id)

        return record_id

    def get(self, record_id: str, deleted: bool = False):
        """
        Fetch
        :param str record_id: The identifier for the record to fetch. This value is compared against the attribute specified in `id_attr`.
        :param bool deleted: Include "deleted" objects in the query
        :return object: An instance of the object type from `model_class`.
        """
        logging.debug("record_id: %s", record_id)
        collection_name = self.collection
        logging.debug("collection_name: %s", collection_name)
        collection = self.mongo.db[collection_name]
        logging.debug("collection: %s", collection)
        id_value = record_id
        if self.id_attr == "_id":
            logging.debug("ID attribute is '_id', converting to ObjectId")
            id_value = ObjectId(record_id)
        logging.debug("id_value: %s", id_value)
        query_filter = {self.id_attr: id_value}
        if not deleted:
            query_filter.update(
                {
                    "$or": [
                        {"deleted_at": Timestamp(0, 0)},
                        {"deleted_at": {"$exists": False}},
                    ]
                }
            )
        logging.debug("query_filter: %s", query_filter)
        record = collection.find_one(filter=query_filter)
        logging.debug("record: %s", record)
        if not record:
            raise ObjectNotFound(f"Record not found where '{self.id_attr}' = '{record_id}'")
        modified_record = self._modify_record(record)
        logging.debug("modified_record: %s", modified_record)
        schema = self.schema_class()
        logging.debug("schema: %s", schema)
        obj = schema.load(modified_record)
        logging.debug("obj: %s", obj)
        return obj

    def query(self, options: QueryOptions, deleted: bool = False):
        """
        :param QueryOptions options: (Optional) Options specifying limits to the query's returned results
        """
        logging.debug("options: %s", options)
        collection_name = self.collection
        logging.debug("collection_name: %s", collection_name)
        collection = self.mongo.db[collection_name]
        logging.debug("collection: %s", collection)
        filters = options.filters.update({"deleted_at": {"$exists": deleted}})
        logging.debug("filters: %s", filters)
        records = collection.find(
            filter=filters,
            projection=options.projection,
            skip=options.skip,
            limit=options.skip,
            sort=options.sort,
        )
        logging.debug("records: %s", records)
        modified_records = map(lambda r: self._modify_record(r), records)
        logging.debug("modified_records: %s", modified_records)
        schema = self.schema_class()
        logging.debug("schema: %s", schema)
        objects = list(map(lambda m: schema.load(m), modified_records))
        logging.debug("objects: %s", objects)
        return objects

    def update(self, obj):
        """ """
        pass

    def delete(self, obj):
        """ """
        pass
