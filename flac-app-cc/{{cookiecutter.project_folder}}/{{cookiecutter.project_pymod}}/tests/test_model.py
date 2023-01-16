import pytest

from {{cookiecutter.project_pymod}}.model import entities as ents


class TestPost:

    def test_insert(self, db):
        post = ents.Post.testing_create()
        assert ents.Post.query.count() == 1
        assert ents.Post.query.first() is post

    def test_repr(self, db):
        post = ents.Post.testing_create(id=99999, title='some title')
        assert str(post) == '<Post 99999: some title>'


class TestComment:

    def test_insert(self, db):
        comment = ents.Comment.testing_create()
        assert ents.Comment.query.count() == 1
        assert ents.Comment.query.first() is comment

    def test_repr(self, db):
        comment = ents.Comment.testing_create(id=99999, title='other title')
        assert str(comment) == '<Comment 99999: other title>'


class TestProduct:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        ents.Product.delete_all()

    def test_unique_and_upsert(self):
        assert ents.Product.query.count() == 0

        ents.Product.upsert(code='0123', per_case=1)
        ents.Product.upsert(code='0123', per_case=2)

        prod = ents.Product.query.one()
        assert prod.per_case == 2
        assert prod.code == '0123'
