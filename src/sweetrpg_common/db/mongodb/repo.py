# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
"""

from ..exceptions import ObjectNotFound
from bson.objectid import ObjectId
import datetime


class MongoDataRepository(object):

    def __init__(self, **kwargs):
        self.model_class = kwargs['model']
        self.schema_class = kwargs['schema']
        self.id_attr = kwargs.get('id_attr') or '_id'
        self.mongo = kwargs.get('mongo')
        self.collection = getattr(self.model_class, '__tablename__')

    def __repr__(self):
        return f"<MongoDataRepository(model_class={self.model_class}, schema_class={self.schema_class}, id_attr={self.id_attr}, collection={self.collection})>"

    def get(self, record_id):
        print(f"record_id: {record_id}")
        collection_name = self.collection
        print(f"collection_name: {collection_name}")
        print(f"self.mongo: {self.mongo}")
        collection = self.mongo.db[collection_name]
        print(f"collection: {collection}")
        record = collection.find_one({self.id_attr: record_id})
        print(f"record: {record}")
        if not record:
            raise ObjectNotFound(f'Record not found where \'{self.id_attr}\' = \'{record_id}\'')
        for k,v in record.items():
            print(f"k: {k}, v: {v}")
            if isinstance(v, ObjectId):
                record[k] = str(v)
            elif isinstance(v, datetime.datetime):
                d = v.replace(tzinfo=datetime.timezone.utc)
                record[k] = d.isoformat(timespec='milliseconds')
        print(f"record: {record}")
        schema = self.schema_class()
        print(f"schema: {schema}")
        obj = schema.load(record)
        print(f"obj: {obj}")
        return obj
