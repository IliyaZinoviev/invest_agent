import dataclasses
import inspect
from datetime import datetime
from functools import partial, wraps
from typing import Any, Callable, Type

import simplejson
from pydantic import BaseModel
from simplejson import JSONEncoder

from source.core.extentions import logger
from source.utils.mixins import Prompt, ReadJson


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, BaseModel):
            return o.dict()
        return super().default(o)


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
    def __init__(self, path: str, input_msg: str, serializer: Type[BaseModel] = None):
        self.input_msg: str = input_msg
        self.path = path
        self.serializer = serializer

    @staticmethod
    async def _write_fn_res_to_json(path, fn: Callable[[], Any]):
        if inspect.iscoroutinefunction(fn):
            res = await fn()
        else:
            res = fn()
        with open(path, 'w') as file:
            simplejson.dump(res, file, cls=EnhancedJSONEncoder)
        return res

    async def _prompt_with_reading_from_json(self, on_writing_fn: Callable[[], Any]):
        on_reading_fn = partial(self.read_json, self.path, self.serializer)
        on_writing_fn_with_json = partial(self._write_fn_res_to_json, self.path, on_writing_fn)
        return await self.prompt(on_reading_fn, on_writing_fn_with_json, self.input_msg)

    def __call__(self, fn):
        @wraps(fn)
        async def wrapper(inst, *args, **kwargs):
            bind_get_stocks_dict_fn = partial(fn, inst, *args, **kwargs)
            return await self._prompt_with_reading_from_json(bind_get_stocks_dict_fn)
        return wrapper
