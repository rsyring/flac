import flask
import flask_sqlalchemy


class Model(flask_sqlalchemy.Model):

    @classmethod
    def _db(cls):
        return flask.current_app.extensions['sqlalchemy'].db

    @classmethod
    def delete_all(cls):
        session = cls._db().session
        cls.query.delete(synchronize_session=False)
        session.commit()
