import logging

import sqlalchemy as sa
from aiopg.sa import create_engine
from sqlalchemy.ext.declarative import declarative_base

from source.app.config import config

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

metadata = sa.MetaData()
Base = declarative_base(metadata=metadata)

session_provider = []
db_engine_provider = []


async def create_db_engine():
    return await create_engine(user=config.DB_USERNAME,
                               database=config.DB_NAME,
                               host=config.DB_HOST,
                               password=config.DB_PASSWORD)
