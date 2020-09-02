import logging

from sqlalchemy_utils import functions as safunc

log = logging.getLogger(__name__)


def create_db(db_url, replace_existing):
    log.info(f'operating on: {db_url}')

    exists = safunc.database_exists(db_url)
    if replace_existing and exists:
        safunc.drop_database(db_url)
        log.info('database dropped')

    if exists:
        log.info('database already exists')
        return

    safunc.create_database(db_url)
    log.info('database created')
