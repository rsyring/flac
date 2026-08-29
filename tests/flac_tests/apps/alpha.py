import datetime as dt
import enum
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import event, orm
from sqlalchemy_utils import ArrowType, EmailType

from flac.app import FlacApp
from flac.contrib.sqlalchemy import (
    DefaultColsMixin,
    FakerMixin,
    MethodsMixin,
    session_execute,
    session_scalars,
)


db = SQLAlchemy()


class AlphaApp(FlacApp):
    @classmethod
    def create(cls, **kwargs):
        return super().create('alpha', Path(__file__).parent, **kwargs)

    def on_app_ready(self):
        db.init_app(self)

        with self.app_context():

            @event.listens_for(db.engine, 'connect')
            def set_sqlite_pragma(dbapi_conn, con_record):
                dbapi_conn.execute('PRAGMA foreign_keys=ON')


class EntityMixin(FakerMixin, MethodsMixin, DefaultColsMixin):
    pass


# Default cascade setting for parent/child relationships.  Should get set on parent side.
# Docs: https://l12.io/sa-parent-child-relationship-config
_rel_cascade = 'all, delete-orphan'


def delete_all():
    User.delete_all()
    Role.delete_all()
    Article.delete_all()
    Tag.delete_all()
    Project.delete_all()
    Bag.delete_all()
    Blog.delete_all()
    Category.delete_all()


class Project(EntityMixin, db.Model):
    __tablename__ = 'project'

    name = sa.Column(sa.String, nullable=False)


class Task(EntityMixin, db.Model):
    __tablename__ = 'task'

    project_id = sa.Column(sa.String, sa.ForeignKey(Project.id, ondelete='cascade'), nullable=False)
    project = orm.relationship(Project, lazy='selectin')

    content = sa.Column(sa.String, nullable=False)
    due = sa.Column(sa.Date)

    @session_execute
    @classmethod
    def select_due(cls):
        return sa.select(cls).where(cls.due <= dt.datetime.now(dt.UTC))

    @session_scalars
    @classmethod
    def select_due2(cls):
        return sa.select(cls).where(cls.due <= dt.datetime.now(dt.UTC))


class Bag(EntityMixin, db.Model):
    __tablename__ = 'bag'

    class Temps(enum.Enum):
        hot = 'hot'
        cold = 'cold'

    name = sa.Column(sa.String, nullable=False)
    order = sa.Column(sa.Integer, nullable=False)
    date = sa.Column(sa.Date, nullable=False)
    datetime = sa.Column(sa.DateTime, nullable=False)
    amount = sa.Column(sa.Numeric(10, 2), nullable=False)
    weight = sa.Column(sa.Float, nullable=False)
    active = sa.Column(sa.Boolean, nullable=False)
    arrow = sa.Column(ArrowType, nullable=False)
    email = sa.Column(EmailType, nullable=False)
    temp = sa.Column(sa.Enum(Temps, name='enum_bag_temps'), nullable=False)
    ident = sa.Column(sa.UUID, nullable=False)

    skip_a = sa.Column(sa.String)
    skip_b = sa.Column(sa.String, nullable=False, default='10')
    skip_c = sa.Column(sa.String, nullable=False, server_default=sa.text('11'))


class Category(EntityMixin, db.Model):
    __tablename__ = 'category'

    name = sa.Column(sa.String, nullable=False)


class Blog(EntityMixin, db.Model):
    __tablename__ = 'blog'

    category_id = sa.Column(sa.String, sa.ForeignKey(Category.id))
    category = orm.relationship(Category, lazy='selectin')

    title = sa.Column(sa.String, nullable=False)


user_role = sa.Table(
    'user_role',
    db.metadata,
    sa.Column(
        'user_id',
        sa.ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        'role_id',
        sa.ForeignKey('role.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class User(EntityMixin, db.Model):
    __tablename__ = 'user'

    name = sa.Column(sa.String, nullable=False)
    roles = orm.relationship(
        'Role',
        secondary=user_role,
        back_populates='users',
        lazy='selectin',
    )


class Role(EntityMixin, db.Model):
    __tablename__ = 'role'

    name = sa.Column(sa.String, nullable=False)
    users = orm.relationship(
        User,
        secondary=user_role,
        back_populates='roles',
        lazy='selectin',
    )


article_tag = sa.Table(
    'article_tag',
    db.metadata,
    sa.Column(
        'article_id',
        sa.ForeignKey('article.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        'tag_id',
        sa.ForeignKey('tag.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class Article(EntityMixin, db.Model):
    __tablename__ = 'article'

    title = sa.Column(sa.String, nullable=False)
    tags = orm.relationship('Tag', secondary=article_tag, lazy='selectin')


class Tag(EntityMixin, db.Model):
    __tablename__ = 'tag'

    name = sa.Column(sa.String, nullable=False)
