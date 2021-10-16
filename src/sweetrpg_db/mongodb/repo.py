# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""MongoDB repository module.
"""

from ..exceptions import ObjectNotFound
from bson.objectid import ObjectId
from bson.timestamp import Timestamp
import datetime
from .options import QueryOptions
from pymongo.write_concern import WriteConcern
import logging
from mongoengine.queryset import QuerySet
from mongoengine import Document


class MongoDataRepository(object):
    """A repository class for interacting with a MongoDB database."""

    def __init__(self, **kwargs):
        """Create a MongoDB repository instance.

        :param kwargs: Keyword arguments for setting up the repository connection.
        :key model: The class of the model for this connection.
        :key document: The class of the document for this connection.
        :key db: A :class:`PyMongo` object used for connecting to the database.
        """
        self.model_class = kwargs["model"]
        self.document_class = kwargs["document"]
        # self.db = kwargs.get("db")
        # print(dir(self.document_class))
        self.collection = kwargs["collection"]  # self.document_class.meta["collection"]

    def __repr__(self):
        return f"<MongoDataRepository(model_class={self.model_class}, document_class={self.document_class}, collection={self.collection})>"

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

    def _adjust_sort(self, sort: tuple) -> str:
        if sort[1] < 0:
            return f"-{sort[0]}"
        return f"+{sort[0]}"

    def create(self, data: dict) -> Document:
        """Inserts a new object in the database with the data provided.

        :param dict data: The data for the object
        :return Document: The inserted document.
        """
        logging.debug("data: %s", data)

        # collection = self.db[self.collection]
        logging.info("Creating new %s record with data %s...", self.document_class.__name__, data)
        doc = self.document_class(**data)
        logging.debug("doc: %s", doc)
        # result = collection.with_options(write_concern=WriteConcern(w=3, j=True)).insert_one(data)
        doc.validate()
        doc.save()
        logging.debug("saved doc: %s", doc)

        return doc

    def get(self, record_id: str, deleted: bool = False) -> Document:
        """Fetch a single record from the database.

        :param str record_id: The identifier for the record to fetch. This value is compared against the attribute specified in `id_attr`.
        :param bool deleted: Include "deleted" objects in the query
        :return Document: An instance of the object type from `model_class`.
        """
        logging.debug("record_id: %s", record_id)
        id_value = record_id
        if isinstance(id_value, str):
            id_value = ObjectId(record_id)
        logging.debug("id_value: %s", id_value)
        query_filter = {"_id": id_value}
        if not deleted:
            query_filter.update({"deleted_at": {"$not": {"$type": "date"}}})
        logging.debug("query_filter: %s", query_filter)

        logging.info("Fetching %s record for ID %s...", self.document_class.__name__, id_value)
        record = self.document_class.objects(__raw__=query_filter).first()  # QuerySet(self.document_class, self.collection)
        # print(f"qs: {qs}")
        # logging.debug("qs: %s", qs)
        # record = None # qs.get(**query_filter)
        logging.debug("record: %s", record)
        # if not record:
        #     raise ObjectNotFound(f"Record not found where for '{record_id}'")

        return record

    def query(self, options: QueryOptions, deleted: bool = False) -> list:
        """Perform a query for objects in the database.

        :param QueryOptions options: (Optional) Options specifying limits to the query's returned results
        :return list: Returns a list of Document-subclass instances matching the query.
        """
        logging.debug("options: %s", options)
        query_filter = options.filters or {}
        if not deleted:
            query_filter.update({"deleted_at": {"$not": {"$type": "date"}}})
        logging.debug("query_filter: %s", query_filter)

        logging.info("Searching for %s records matching filter %s...", self.document_class, query_filter)
        records = (
            self.document_class.objects(__raw__=query_filter)
            .order_by(*list(map(self._adjust_sort, options.sort)))
            .skip(options.skip)
            .limit(options.limit)
            .only(*options.projection)
        )
        # qs = QuerySet(self.document_class, self.collection)
        # if options.skip > 0:
        #     qs.skip(options.skip)
        # if options.limit > 0:
        #     qs.limit(options.limit)
        # if len(options.projection) > 0:
        #     qs.only(*options.projection)
        # if len(options.sort) > 0:
        #     qs.order_by(*options.sort)
        # print(f"qs: {qs}")
        # logging.debug("qs: %s", qs)
        # query_set = self.document_class.objects.skip(options.skip).limit(options.limit).order_by(options.sort).only(*options.projection)
        # records = list(qs.all())  # .all()
        logging.debug("records: %s", records)

        # modified_records = map(self._modify_record, records)
        # logging.debug("modified_records: %s", modified_records)

        return list(records)

    def update(self, record_id: str, update: dict, deleted: bool = False) -> Document:
        """Update the specified record.

        :param str record_id: The ID of the record to update.
        :param dict update: The data to update for the record.
        :param bool deleted: Indicates whether the update operation should look for deleted records.
        :return Document: The update version of the object.
        """
        id_value = record_id
        if isinstance(id_value, str):
            id_value = ObjectId(record_id)
        # if self.id_attr == "_id":
        #     logging.debug("ID attribute is '_id', converting to ObjectId")
        #     id_value = ObjectId(record_id)
        obj_filter = {"_id": id_value}
        logging.debug("obj_filter: %s", obj_filter)

        update_oper = {"$set": update}
        logging.debug("update_oper: %s", update_oper)

        logging.info("Marking %s record %s deleted...", self.model_class, id_value)
        query_filter = {"_id": id_value}
        if not deleted:
            query_filter.update({"deleted_at": {"$not": {"$type": "date"}}})
        logging.debug("query_filter: %s", query_filter)
        # doc = self.document_class.objects.raw(query_filter).update(update_oper)
        doc = self.get(record_id, deleted=deleted)
        # if doc is None:
        #     logging.info("No document found to update for record ID %s.", record_id)
        #     return False
        logging.debug("doc: %s", doc)
        doc.update(**update)

        return doc

    def delete(self, record_id: str, actually: bool = False) -> bool:
        """'Delete' the specified record. Deletion is accomplished by setting the `deleted_at` field to the current
            timestamp, so that queries for the object will ignore it.

        :param str record_id: The record ID of the object to delete. This can be a string or :class:`bson.objectid.ObjectId`.
        :param bool actually: Actually delete the record instead of just marking it "deleted".
        :return bool: A boolean indicating whether the record was able to be marked deleted.
        :raises DoesNotExist:
        """
        id_value = record_id
        if isinstance(id_value, str):
            id_value = ObjectId(record_id)
        doc = self.get(record_id)
        # if doc is None:
        #     logging.info("No document found to delete for record ID %s.", record_id)
        #     return False

        if actually:
            logging.info("Deleting %s record %s...", self.model_class.__name__, id_value)
            doc.delete()
            return True
        else:
            logging.info("Marking %s record %s deleted...", self.model_class.__name__, id_value)
            now = datetime.datetime.utcnow()
            doc.deleted_at = now
            updated_doc = doc.save()
            logging.debug("updated_doc: %s", updated_doc)

            return True

        return False
