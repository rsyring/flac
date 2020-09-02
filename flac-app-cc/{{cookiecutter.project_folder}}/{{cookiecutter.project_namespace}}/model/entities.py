import sqlalchemy as sa
from sqlalchemy import orm

from .utils import EntityMixin
from {{cookiecutter.project_namespace}}.ext import db

# Default cascade setting for parent/child relationships.  Should get set on parent side.
# Docs: https://l12.io/sa-parent-child-relationship-config
_rel_cascade = 'all, delete-orphan'


class Post(EntityMixin, db.Model):
    __tablename__ = 'posts'

    title = sa.Column(sa.String, nullable=False)
    author = sa.Column(sa.String, nullable=False)
    body = sa.Column(sa.String, nullable=False)

    comments = orm.relationship('Comment', cascade=_rel_cascade, passive_deletes=True)

    def __repr__(self):
        return f'<Post {self.id}: {self.title[0:50]}>'


class Comment(EntityMixin, db.Model):
    __tablename__ = 'comments'

    title = sa.Column(sa.String, nullable=False)
    author = sa.Column(sa.String, nullable=False)
    body = sa.Column(sa.String, nullable=False)

    post_id = sa.Column(sa.Integer, sa.ForeignKey(Post.id, ondelete='cascade'), nullable=False)
    post = orm.relationship(Post)

    def __repr__(self):
        return f'<Comment {self.id}: {self.title[0:50]}>'

    @classmethod
    def testing_create(cls, **kwargs):
        if 'post' not in kwargs and 'post_id' not in kwargs:
            kwargs['post'] = Post.testing_create()

        return super().testing_create(**kwargs)


class Product(EntityMixin, db.Model):
    __tablename__ = 'products'
    __upsert_index_elements__ = ('code',)

    code = sa.Column(sa.String, nullable=False, unique=True)
    per_case = sa.Column(sa.Integer)
