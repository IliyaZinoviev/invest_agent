import asyncio
from datetime import datetime
from functools import wraps
from time import time

from source.app.extentions import logger


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


def timeit(f):
    if asyncio.iscoroutinefunction(f):
        @wraps(f)
        async def wrap(*args, **kw):
            ts = time()
            result = await f(*args, **kw)
            te = time()
            interval = te - ts
            logger.debug('func:%r took: %2.4f sec' % (f.__name__, interval))
            return result
    else:
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            interval = te - ts
            logger.debug('func:%r took: %2.4f sec' % (f.__name__, interval))
            return result

    return wrap
