try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    # TODO: this doesn't work as expected.  flask_sqlalchemy is installed due to
    # flac dependency even though setup.py says that should only be installed with an
    # extra.
    class SQLAlchemy:
        def init_app(self, app):
            pass


db = SQLAlchemy()


def init_ext(app):
    db.init_app(app)
