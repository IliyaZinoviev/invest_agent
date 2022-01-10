from typing import Any, Callable

import simplejson
from pydantic import BaseModel


class ReadJson:

    @staticmethod
    def read_json(path, serializer: BaseModel = None):
        with open(path, 'r') as file:
            data = simplejson.load(file)
            if serializer:
                if isinstance(data, dict):
                    res = serializer.parse_obj(data).__root__
            else:
                res = data
            return res


class Prompt:

    @staticmethod
    async def prompt(on_reading_fn: Callable[[], Any], on_rewriting_fn: Callable[[], Any], input_msg: str):
        while True:
            try:
                reading_flag = input(input_msg)
                assert reading_flag in ['r', 'w'], 'Only [r/w] are available!'
            except Exception:
                pass
            if reading_flag == 'r':
                return on_reading_fn()
            elif reading_flag == 'w':
                return await on_rewriting_fn()
