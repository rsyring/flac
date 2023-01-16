try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    class SQLAlchemy:
        def init_app(self, app):
            pass


db = SQLAlchemy()


def init_ext(app):
    db.init_app(app)
