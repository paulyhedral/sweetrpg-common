# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
"""

from ..exceptions import ObjectNotFound
from bson.objectid import ObjectId
import datetime
from .options import QueryOptions
from pymongo.write_concern import WriteConcern


class MongoDataRepository(object):
    """
    """

    def __init__(self, **kwargs):
        """
        """
        self.model_class = kwargs['model']
        self.schema_class = kwargs['schema']
        self.id_attr = kwargs.get('id_attr') or '_id'
        self.mongo = kwargs.get('mongo')
        self.collection = getattr(self.model_class, '__tablename__')

    def __repr__(self):
        return f"""
        <MongoDataRepository(model_class={self.model_class},
                             schema_class={self.schema_class},
                             id_attr={self.id_attr},
                             collection={self.collection})>
        """

    def _handle_value(self, value):
        """
        """
        if isinstance(value, ObjectId):
            print(f"converting ObjectId('{value}')...")
            return str(value)
        elif isinstance(value, datetime.datetime):
            print(f"converting datetime value '{value}'...")
            d = value.replace(tzinfo=datetime.timezone.utc)
            return d.isoformat(timespec='milliseconds')
        elif isinstance(value, list):
            print(f"converting list '{value}'...")
            return list(map(lambda v: self._handle_value(v), value))

        print(f"returning unprocessed value '{value}'...")
        return value

    def _modify_record(self, record:dict) -> dict:
        """
        """
        modified_record = {}
        for k,v in record.items():
            print(f"k: {k}, v: {v}")
            if k == '_id':
                k = 'id'
            modified_value = self._handle_value(v)
            modified_record[k] = modified_value
            print(f"k: {k}, v (modified): {modified_value}")

        return modified_record

    def create(self, data:dict):
        """
        """
        print(f"data: {data}")
        collection_name = self.collection
        print(f"collection_name: {collection_name}")
        # session = self.mongo.cx.start_session()
        # print(f"session: {session}")
        # session.start_transaction(write_concern=WriteConcern(j=True))
        collection = self.mongo.db[collection_name]
        print(f"collection: {collection}")
        result = collection.with_options(write_concern=WriteConcern(j=True)).insert_one(data)
        print(f"result: {result}")
        # session.commit_transaction()
        record_id = result.inserted_id
        print(f"record_id: {record_id}")
        record = self.get(record_id)
        print(f"record: {record}")
        # session.end_session()

        return record

    def get(self, record_id:str, deleted:bool=False):
        """
        :param str record_id: The identifier for the record to fetch. This value is compared against the attribute specified in `id_attr`.
        :param bool deleted:
        :return object: An instance of the object type from `model_class`.
        """
        print(f"record_id: {record_id}")
        collection_name = self.collection
        print(f"collection_name: {collection_name}")
        collection = self.mongo.db[collection_name]
        print(f"collection: {collection}")
        id_value = record_id
        if self.id_attr == '_id':
            print(f"ID attribute is '_id', converting to ObjectId")
            id_value = ObjectId(record_id)
        print(f"id_value: {id_value}")
        record = collection.find_one({self.id_attr: id_value, 'deleted_at': { '$exists': deleted }})
        print(f"record: {record}")
        if not record:
            raise ObjectNotFound(f'Record not found where \'{self.id_attr}\' = \'{record_id}\'')
        modified_record = self._modify_record(record)
        print(f"modified_record: {modified_record}")
        schema = self.schema_class()
        print(f"schema: {schema}")
        obj = schema.load(modified_record)
        print(f"obj: {obj}")
        return obj

    def query(self, options:QueryOptions, deleted:bool=False):
        """
        :param QueryOptions options: (Optional) Options specifying limits to the query's returned results
        """
        print(f"options: %s", options)
        collection_name = self.collection
        print(f"collection_name: {collection_name}")
        collection = self.mongo.db[collection_name]
        print(f"collection: {collection}")
        filters = options.filters.update({'deleted_at': { '$exists': deleted }})
        print(f"filters: {filters}")
        records = collection.find(filter=filters, projection=options.projection, skip=options.skip, limit=options.skip, sort=options.sort)
        print(f"records: {records}")
        modified_records = map(lambda r: self._modify_record(r), records)
        print(f"modified_records: {modified_records}")
        schema = self.schema_class()
        print(f"schema: {schema}")
        objects = list(map(lambda m: schema.load(m), modified_records))
        print(f"objects: {objects}")
        return objects

    def update(self, obj):
        """
        """
        pass

    def delete(self, obj):
        """
        """
        pass
