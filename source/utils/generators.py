from asyncio import sleep
from datetime import datetime

from source.app.extentions import logger


async def limit_iter(struct, delay, limit):
    struct_length = len(struct)
    struct_part_count = struct_length // limit
    if struct_length < limit or (struct_length % limit != 0 and struct_length > limit):
        struct_part_count += 1
    ind = 0
    while ind < struct_part_count:
        yield ind
        start = datetime.now()
        if struct_length != len(struct):
            struct_length = len(struct)
            struct_part_count = struct_length // limit
            if struct_length < limit or (struct_length % limit != 0 and struct_length > limit):
                struct_part_count += 1
        ind += 1
        end = datetime.now() - start
        curr_delay = delay - end.total_seconds()
        logger.info(f'{curr_delay=}')
        if ind != struct_part_count:
            await sleep(curr_delay)
