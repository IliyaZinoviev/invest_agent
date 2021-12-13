from datetime import datetime
from time import sleep

from source.core.extentions import logger


def limit_iter(struct, delay, parts_count):
    struct_length = len(struct)
    curr_parts_count = struct_length // parts_count
    if struct_length < parts_count or (struct_length % parts_count != 0 and struct_length > parts_count):
        curr_parts_count += 1
    ind = 0
    while ind < curr_parts_count:
        start = datetime.now()
        yield ind
        logger.info(f'{(struct_length != len(struct))=}')
        if struct_length != len(struct):
            struct_length = len(struct)
            curr_parts_count = struct_length // parts_count
            if struct_length < parts_count or (struct_length % parts_count != 0 and struct_length > parts_count):
                curr_parts_count += 1
        ind += 1
        end = datetime.now() - start
        curr_delay = delay - end.total_seconds()
        logger.info(curr_delay)
        if curr_delay > 0 and ind + 1 != curr_parts_count:
            sleep(curr_delay)
