# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
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
        :key model: The class of the model for this connection.
        :key document: The class of the document used for deserializing objects from the database.
        :key db: A :class:`PyMongo` object used for connecting to the database.
        """
        self.model_class = kwargs["model"]
        self.document_class = kwargs["document"]
        self.db = kwargs.get("db")
        # self.collection = getattr(self.model_class, "__tablename__")

    def __repr__(self):
        return f"""\
        <MongoDataRepository(document_class={self.document_class})>
        """

    def _handle_value(self, value):
        """Convert a value to a string.

        :param any value: The value to convert. Supports :class:`bson.objectid.ObjectId`,
            :class:`datetime.datetime`, :class:`bson.timestamp.Timestamp`, and lists of
            any of those types.
        :return str: A string of the specified value.
        """
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
            return list(map(self._handle_value, value))

        logging.debug("returning unprocessed value '%s'...", value)
        return value

    def _modify_record(self, record: dict) -> dict:
        """Modify a record by converting any values to strings, and renaming the internal '_id'
            field to 'id'.

        :param dict record: The record to modify.
        :return dict: The modified record.
        """
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
        :return MongoModel: The inserted document.
        """
        logging.debug("self: %s, data: %s", self, data)
        # collection_name = self.collection
        # logging.debug("collection_name: %s", collection_name)
        # collection = self.db.db[collection_name]
        # logging.debug("collection: %s", collection)

        logging.info("Creating new %s record with data %s...", self.document_class, data)
        document = self.document_class(**data)
        logging.debug("self: %s, document: %s", self, document)
        # result = collection.with_options(write_concern=WriteConcern(w=3, j=True)).insert_one(data)
        result = document.save()
        logging.debug("result: %s, document: %s", result, document)
        # if result is None:
        #     return None
        # record_id = result.inserted_id
        # logging.debug("record_id: %s", record_id)

        return document

    def get(self, record_id: str, deleted: bool = False):
        """Fetch a single record from the database.

        :param str record_id: The identifier for the record to fetch. This value is compared against the attribute specified in `id_attr`.
        :param bool deleted: Include "deleted" objects in the query
        :return object: An instance of the object type from `model_class`.
        """
        # logging.debug("record_id: %s", record_id)
        # collection_name = self.collection
        # logging.debug("collection_name: %s", collection_name)
        # collection = self.db.db[collection_name]
        # logging.debug("collection: %s", collection)
        id_value = record_id
        if isinstance(id_value, str):
            # if self.id_attr == "_id":
            #     logging.debug("ID attribute is '_id', converting to ObjectId")
            id_value = ObjectId(record_id)
        logging.debug("id_value: %s", id_value)
        query_filter = {"_id": id_value}
        if not deleted:
            query_filter.update({"deleted_at": {"$not": {"$type": "date"}}})
        logging.debug("query_filter: %s", query_filter)

        logging.info("Fetching %s record for ID %s...", self.model_class, id_value)
        # record = collection.find_one(filter=query_filter)
        record = self.document_class.objects.raw(query_filter).first()
        logging.debug("record: %s", record)
        if not record:
            raise ObjectNotFound(f"Record not found where for '{record_id}'")

        modified_record = self._modify_record(record)
        logging.debug("modified_record: %s", modified_record)
        # schema = self.schema_class()
        # logging.debug("schema: %s", schema)
        # obj = schema.load(modified_record)
        # logging.debug("obj: %s", obj)
        return modified_record

    def query(self, options: QueryOptions, deleted: bool = False):
        """Perform a query for objects in the database.

        :param QueryOptions options: (Optional) Options specifying limits to the query's returned results
        """
        logging.debug("options: %s", options)
        # collection_name = self.collection
        # logging.debug("collection_name: %s", collection_name)
        # collection = self.db.db[collection_name]
        # logging.debug("collection: %s", collection)
        query_filter = options.filters
        if not deleted:
            query_filter.update({"deleted_at": {"$not": {"$type": "date"}}})
        logging.debug("query_filter: %s", query_filter)

        logging.info("Searching for %s records matching filter %s...", self.model_class, query_filter)
        query_set = self.document_class.objects
        query_set.skip(options.skip)
        query_set.limit(options.limit)
        query_set.order_by(options.sort)
        records = query_set.all()
        # records = collection.find(
        #     filter=query_filter,
        #     projection=options.projection,
        #     skip=options.skip,
        #     limit=options.skip,
        #     sort=options.sort,
        # )
        logging.debug("records: %s", records)

        modified_records = map(self._modify_record, records)
        logging.debug("modified_records: %s", modified_records)
        # schema = self.schema_class()
        # logging.debug("schema: %s", schema)
        # objects = list(map(schema.load, modified_records))
        # logging.debug("objects: %s", objects)

        return modified_records

    def update(self, record_id: str, update: dict):
        """Update the specified record.

        :param str record_id: The ID of the record to update.
        :param dict update: The data to update for the record.
        :return bool: A boolean indicating whether the record was able to be updated.
        """
        collection_name = self.collection
        logging.debug("collection_name: %s", collection_name)
        collection = self.db.db[collection_name]
        logging.debug("collection: %s", collection)

        id_value = record_id
        if self.id_attr == "_id":
            logging.debug("ID attribute is '_id', converting to ObjectId")
            id_value = ObjectId(record_id)
        obj_filter = {"_id": id_value}
        logging.debug("obj_filter: %s", obj_filter)

        update_oper = {"$set": update}
        logging.debug("update_oper: %s", update_oper)

        logging.info("Marking %s record %s deleted...", self.model_class, id_value)
        result = collection.update_one(filter=obj_filter, update=update_oper)
        logging.debug("result: %s", result)

        if result.matched_count == 1 and result.modified_count == 1:
            return True

        return False

    def delete(self, record_id: str):
        """'Delete' the specified record. Deletion is accomplished by setting the `deleted_at` field to the current
            timestamp, so that queries for the object will ignore it.

        :param str record_id: The record ID of the object to delete. This can be a string or :class:`bson.objectid.ObjectId`.
        :return bool: A boolean indicating whether the record was able to be marked deleted.
        """
        collection_name = self.collection
        logging.debug("collection_name: %s", collection_name)
        collection = self.db.db[collection_name]
        logging.debug("collection: %s", collection)

        id_value = record_id
        if self.id_attr == "_id":
            logging.debug("ID attribute is '_id', converting to ObjectId")
            id_value = ObjectId(record_id)
        obj_filter = {"_id": id_value}
        logging.debug("obj_filter: %s", obj_filter)
        now = datetime.datetime.utcnow()
        update_oper = {"$set": {"deleted_at": now}}
        logging.debug("update_oper: %s", update_oper)

        logging.info("Marking %s record %s deleted...", self.model_class, id_value)
        result = collection.update_one(filter=obj_filter, update=update_oper)
        logging.debug("result: %s", result)

        if result.matched_count == 1 and result.modified_count == 1:
            return True

        return False
