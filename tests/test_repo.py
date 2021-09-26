# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from sweetrpg_db.mongodb.repo import MongoDataRepository
from sweetrpg_db.mongodb.options import QueryOptions
from sweetrpg_db.schema.base import BaseSchema
from pymongo import IndexModel, MongoClient
import os
from dotenv import load_dotenv
import pytest
from bson.objectid import ObjectId
from mongoengine import connect, Document, fields


load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]


class TestModel(object):
    pass


class TestSchema(BaseSchema):
    pass


class TestDocument(Document):
    meta = {
        "collection": "exams",
        "indexes": [{"name":"exam_name", "fields":["name"]}],
        "strict": False,
        "db_alias": "unit-tests",
    }

    name = fields.StringField(required=True)
    score = fields.IntField(min_value=0, max_value=100, default=0)

    def __repr__(self):
        return f"<TestDocument(name={self.name}, score={self.score})>"


@pytest.fixture(scope="session", autouse=True)
def setup_repo(request):
    # db = MongoClient(host=MONGODB_URI)
    connect(host=MONGODB_URI, alias="unit-tests")
    repo = MongoDataRepository(model=TestModel, document=TestDocument, collection="exams")
    request.session.repo = repo
    request.session.object_ids = []


def teardown_test_docs(request):
    db = MongoClient(host=MONGODB_URI)
    db["exams"].delete_many({})


def test_create(request):
    data = {"name": "Pop Quiz", "score": 99}
    doc = request.session.repo.create(data)
    assert doc is not None
    assert isinstance(doc, TestDocument)
    request.session.object_ids.append(doc.pk)


@pytest.mark.run(after="test_create")
def test_get(request):
    id = ObjectId(request.session.object_ids[0])
    doc = request.session.repo.get(id)
    assert doc is not None
    assert isinstance(doc, TestDocument)


@pytest.mark.run(after="test_create")
def test_query_all(request):
    options = QueryOptions()
    docs = request.session.repo.query(options)
    assert docs is not None
    assert len(docs) >= len(request.session.object_ids)


@pytest.mark.run(after="test_create")
def test_query_deleted(request):
    data = {"name": "Delete Me", "score": 86}
    doc = request.session.repo.create(data)
    assert doc is not None
    success = request.session.repo.delete(doc.pk)
    assert success
    options = QueryOptions()
    deleted_docs = request.session.repo.query(options, deleted=True)
    assert deleted_docs is not None
    assert len(deleted_docs) >= 1


@pytest.mark.run(after="test_create")
def test_query_filtered(request):
    options = QueryOptions(filters={"score": {"$eq": 99}})
    docs = request.session.repo.query(options)
    assert docs is not None
    assert len(docs) >= 1


@pytest.mark.run(after="test_create")
def test_query_sorted(request):
    data = [{"name": "Second", "score": 20}, {"score": 30, "name": "Third"}, {"name": "First", "score": 10}]
    for datum in data:
        created = request.session.repo.create(datum)
        assert created is not None
    options = QueryOptions(sort=[("score", 1)])
    docs = request.session.repo.query(options)
    assert docs is not None
    assert len(docs) >= 3
    print(f"docs: {docs}")
    sorted_properly = True
    last_score = -999
    for d in docs:
        print(f"d: {d}")
        if d.score < last_score:
            sorted_properly = False
            break
        last_score = d.score
    assert sorted_properly


@pytest.mark.run(after="test_create")
def test_query_with_projections(request):
    options = QueryOptions(projection=["score"])
    docs = request.session.repo.query(options)
    assert docs is not None
    for d in docs:
        assert d.name is None
        assert d.score is not None


@pytest.mark.run(after="test_query_all")
def test_update(request):
    id = ObjectId(request.session.object_ids[0])
    updated_doc = request.session.repo.update(id, {"score": 22})
    assert updated_doc is not None


@pytest.mark.run("last")
def test_delete(request):
    object_ids = request.session.object_ids
    deleted = 0
    for id in object_ids:
        request.session.repo.delete(id, actually=True)
        deleted += 1
    assert deleted == len(object_ids)
