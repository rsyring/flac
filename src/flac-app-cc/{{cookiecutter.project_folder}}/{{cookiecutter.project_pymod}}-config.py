import os


def db_uri(suffix=''):
    if 'CI' in os.environ:
        return 'postgresql://postgres@localhost/postgres'

    return f'postgresql://postgres@localhost:54321/{{cookiecutter.project_dashed}}{suffix}'


def development_config(app, config):
    config['SQLALCHEMY_DATABASE_URI'] = db_uri()

    return config


def testing_config(app, config):
    config['SQLALCHEMY_DATABASE_URI'] = db_uri('_tests')

    return config
