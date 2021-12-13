from datetime import datetime
from functools import wraps, partial
from typing import Callable, Any

import simplejson
from source.core.extentions import logger
from source.utils.mixins import ReadJson, Prompt


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


class JsonPromptDecorator(Prompt, ReadJson):
    def __init__(self, path: str, input_msg: str):
        self.input_msg: str = input_msg
        self.path = path

    @staticmethod
    async def _write_fn_res_to_json(path, fn: Callable[[], Any]):
        res = await fn()
        with open(path, 'w') as file:
            simplejson.dump(res, file)
        return res

    @classmethod
    async def _prompt_with_reading_from_json(cls, path, on_writing_fn: Callable[[], Any], input_msg):
        on_reading_fn = partial(cls.read_json, path)
        on_writing_fn_with_json = partial(cls._write_fn_res_to_json, path, on_writing_fn)
        return await cls.prompt(on_reading_fn, on_writing_fn_with_json, input_msg)

    def __call__(self, fn):
        @wraps(fn)
        async def wrapper(inst, *args, **kwargs):
            bind_get_stocks_dict_fn = partial(fn, inst, *args, **kwargs)
            return await self._prompt_with_reading_from_json(self.path, bind_get_stocks_dict_fn, self.input_msg)
        return wrapper
