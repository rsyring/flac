import datetime as dt
import math
import random
import uuid
from decimal import Decimal

import arrow
import flask
import flask_sqlalchemy as fsa
import sqlalchemy as sa
import sqlalchemy.ext.compiler
import sqlalchemy.types
import wrapt
from blazeutils.strings import randchars
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import insert as pgsql_insert
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import expression
from sqlalchemy_utils import ArrowType, EmailType


def flask_db() -> fsa.SQLAlchemy:
    return flask.current_app.extensions['sqlalchemy']


class utcnow(expression.FunctionElement):
    type = sqlalchemy.types.DateTime()


@sqlalchemy.ext.compiler.compiles(utcnow, 'postgresql')
def _pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@sqlalchemy.ext.compiler.compiles(utcnow, 'mssql')
def _ms_utcnow(element, compiler, **kw):
    return "GETUTCDATE()"


@sqlalchemy.ext.compiler.compiles(utcnow, 'sqlite')
def _sqlite_utcnow(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"


@wrapt.decorator
def _kwargs_match_entity(wrapped, instance, args, kwargs):
    """
    Asserts that the kwargs passed to the wrapped method match the columns/relationships
    of the entity.
    """
    if kwargs.get('_check_kwargs', True):
        insp = sa.inspection.inspect(instance)

        # Only allow kwargs that correspond to a column or relationship on the entity
        allowed_keys = {col.key for col in insp.columns} | set(insp.relationships.keys())

        # Ignore kwargs starting with "_"
        kwarg_keys = set(key for key in kwargs if not key.startswith('_'))
        extra_kwargs = kwarg_keys - allowed_keys
        assert (
            not extra_kwargs
        ), 'Unknown column or relationship names in kwargs: {kwargs!r}'.format(
            kwargs=sorted(extra_kwargs)
        )

    return wrapped(*args, **kwargs)


def _keyword_optional(keyword, before=False, after=False, keep_keyword=False, when_missing=False):
    """Execute a function before and after the decorated function if the keyword
    is in the kwargs
    Examples:
        def do_thing():
            # ... does something ...
        @keyword_optional('_do_thing', before=do_thing)
        def func(data):
            return data
        func(data, _do_thing=True)
    """

    @wrapt.decorator
    def _execute(wrapped, instance, args, kwargs):
        do_it = (
            kwargs.get(keyword, when_missing) if keep_keyword else kwargs.pop(keyword, when_missing)
        )

        if before and do_it:
            before()

        result = wrapped(*args, **kwargs)

        if after and do_it:
            after()

        return result

    return _execute


def random_numeric(column):
    fractional_digits = column.type.scale
    whole_digits = column.type.precision - fractional_digits

    # only use about half the digits to make arithmetic done with this less likely to overflow
    max_whole = 10 ** math.ceil(whole_digits / 2.0) - 1

    whole = random.randint(-max_whole, max_whole)

    fractional = Decimal(random.randint(0, 10**fractional_digits - 1)) / 10**fractional_digits
    return fractional + whole


def randemail(length, randomizer=randchars):
    """Generate a random email address at the given length.
    :param length: must be at least 7 or the function will throw a ValueError.
    :param randomizer: is a function for generating random characters. It must have an identical
                      interface to `randchars`. The default function is `randchars`.
    """
    if length < 7:
        raise ValueError('length must be at least 7')

    half = (length - 2 - 3) / 2.0  # 2 characters for @ and . and 3 for TLD
    return (
        randomizer(int(math.floor(half)), 'alphanumeric')
        + '@'
        + randomizer(int(math.ceil(half)), 'alphanumeric')
        + '.'
        + randomizer(3, 'alpha')
    )


def random_date(start=dt.date(1900, 1, 1), end=dt.date(1900, 12, 31)):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + dt.timedelta(seconds=random_second)


def session_commit():
    try:
        flask_db().session.commit()
    except Exception:
        flask_db().session.rollback()
        raise


def session_flush():
    try:
        flask_db().session.flush()
    except Exception:
        flask_db().session.rollback()
        raise


might_commit = _keyword_optional('_commit', after=session_commit, when_missing=True)
might_flush = _keyword_optional('_flush', after=session_flush)


class DefaultColsMixin:
    id = sa.Column('id', sa.Integer, primary_key=True)
    created_utc = sa.Column(
        ArrowType, nullable=False, default=arrow.utcnow, server_default=utcnow()
    )
    updated_utc = sa.Column(
        ArrowType,
        nullable=False,
        default=arrow.utcnow,
        onupdate=arrow.utcnow,
        server_default=utcnow(),
    )


class MethodsMixin:
    @classmethod
    def _db(cls):
        return flask.current_app.extensions['sqlalchemy']

    @classmethod
    def delete_all(cls):
        session = cls._db().session
        cls.query.delete(synchronize_session=False)
        session.commit()

    @classmethod
    def upsert(cls, values=None, on_conflict_do='update', index_elements=None, **kwargs):
        if index_elements is None:
            index_elements = cls.__upsert_index_elements__

        if values is None:
            values = kwargs

        primary_key_col = inspect(cls).primary_key[0]
        stmt = pgsql_insert(cls.__table__).returning(primary_key_col).values(**values)

        assert on_conflict_do in ('nothing', 'update')
        if on_conflict_do == 'update':
            stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=values)
        else:
            stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)

        result = cls._db().session.execute(stmt)

        return result.scalar()

    @classmethod
    def insert(cls, values=None, **kwargs):
        if values is None:
            values = kwargs

        stmt = pgsql_insert(cls.__table__).values(**values)
        cls._db().session.execute(stmt)

    @classmethod
    def get_by(cls, **kwargs):
        """Returns the instance of this class matching the given criteria or
        None if there is no record matching the criteria.
        If multiple records are returned, an exception is raised.
        """
        return cls.query.filter_by(**kwargs).one_or_none()

    @_kwargs_match_entity
    @classmethod
    def testing_data(cls, **kwargs):
        """Create an object for testing with default data appropriate for the field type
        * Will automatically set most field types ignoring those passed in via kwargs.
        * Subclasses that have foreign key relationships should setup those relationships before
          calling this method.
        Special kwargs:
        _numeric_defaults_range: a tuple of (HIGH, LOW) which controls the acceptable defaults of
                                 the two number types. Both integer and numeric (float) fields are
                                 controlled by this setting.
        """

        numeric_range = kwargs.pop('_numeric_defaults_range', None)

        insp = sa.inspection.inspect(cls)

        def skippable(column):
            return (
                column.key in kwargs
                or column.foreign_keys
                or column.server_default
                or column.default
                or column.primary_key
                or column.nullable
            )

        for column in (col for col in insp.columns if not skippable(col)):
            kwargs[column.key] = cls.random_data_for_column(column, numeric_range)

        return kwargs

    @_kwargs_match_entity
    @classmethod
    def testing_create(cls, **kwargs):
        return cls.add(**cls.testing_data(**kwargs))

    @might_commit
    @might_flush
    @classmethod
    def add(cls, **kwargs):
        obj = cls(**kwargs)
        cls._db().session.add(obj)
        return obj

    @classmethod
    def random_data_for_column(cls, column, numeric_range):
        if 'randomdata' in column.info:
            if type(column.info['randomdata']) is str:
                # assume randomdata the is name of a method on the class
                callable = getattr(cls, column.info['randomdata'])
                data = callable()
                return data

            return column.info['randomdata']()

        default_range = (-100, 100) if numeric_range is None else numeric_range
        if isinstance(column.type, sa.types.Enum):
            return random.choice(column.type.enums)
        elif isinstance(column.type, sa.types.Boolean):
            return random.choice([True, False])
        elif isinstance(column.type, sa.types.Integer):
            return random.randint(*default_range)
        elif isinstance(column.type, sa.types.Float):
            return random.uniform(*default_range)
        elif isinstance(column.type, sa.types.Numeric):
            if numeric_range is not None or column.type.scale is None:
                return random.uniform(*default_range)
            return random_numeric(column)
        elif isinstance(column.type, sa.types.Date):
            return dt.date.today()
        elif isinstance(column.type, sa.types.DateTime):
            return dt.datetime.utcnow()
        elif isinstance(column.type, ArrowType):
            return arrow.utcnow()
        elif isinstance(column.type, EmailType):
            return randemail(min(column.type.length or 50, 50))
        # elif isinstance(column.type, columns.TimeZoneType):
        #     return random.choice(pytz.common_timezones)
        elif isinstance(column.type, (sa.types.String, sa.types.Unicode)):
            return randchars(min(column.type.length or 25, 25))
        elif isinstance(column.type, UUID):
            return uuid.uuid4()

        raise ValueError(f'No randomization for this column available {column}')
