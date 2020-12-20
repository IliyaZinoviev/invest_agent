from datetime import datetime
from functools import wraps

from extentions import logger


def atimeit(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        start = datetime.now()
        logger.info(f'{fn.__name__}(): start: {start}')
        result = await fn(*args, **kwargs)
        end = datetime.now()
        logger.info(f'{fn.__name__}(): end: {end}')
        logger.info(f'{fn.__name__}(): time: {(end - start).total_seconds()}s')
        return result
    return wrapper
