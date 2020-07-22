import logging

from sqlalchemy_utils import functions as safunc

log = logging.getLogger(__name__)


def create_db(db_url, replace_existing):
    if replace_existing and safunc.database_exists(db_url):
        safunc.drop_database(db_url)
        log.info('database dropped')

    safunc.create_database(db_url)
    log.info('database created')
