from flask_sqlalchemy import SQLAlchemy
from flac.model import Model

db = SQLAlchemy(model_class=Model)


def init_app(app):
    db.init_app(app)
