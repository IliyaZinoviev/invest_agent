import inspect
from asyncio import iscoroutine
from dataclasses import dataclass
from functools import partial, wraps
from typing import Type, Callable, Any

import simplejson
from pydantic import BaseModel

from type_aliases import FullyAppicatedFunc
from utils.json.encoder import EnhancedJSONEncoder
from utils.mixins import Prompt
from utils.json.mixins import ReadJson


@dataclass
class JsonFileMetaData:
    def __init__(self, name: str):
        self.name: str = name
        self.path: str = f'../json/{name}.json'


class JsonPromptDecorator(Prompt, ReadJson):
    def __init__(self, path: str, input_msg: str, serializer: Type[BaseModel] = None):
        self.input_msg: str = input_msg
        self.path = path
        self.serializer = serializer

    @staticmethod
    async def _write_fn_res_to_json(path, fn: FullyAppicatedFunc):
        if iscoroutine(fn):
            res = await fn()
        else:
            res = fn()
        with open(path, 'w') as file:
            simplejson.dump(res, file, cls=EnhancedJSONEncoder)
        return res

    async def _prompt_with_reading_from_json(self, fn: FullyAppicatedFunc):
        on_reading_fn = partial(self.read_json, self.path, self.serializer)
        on_writing_fn= partial(self._write_fn_res_to_json, self.path, fn)
        return await self.prompt(on_reading_fn, on_writing_fn, fn, self.input_msg)

    def __call__(self, fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            bind_get_stocks_dict_fn = partial(fn, *args, **kwargs)
            return await self._prompt_with_reading_from_json(bind_get_stocks_dict_fn)
        return wrapper