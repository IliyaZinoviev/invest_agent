from typing import Callable, Any

import simplejson


class ReadJson:

    @staticmethod
    def read_json(path):
        with open(path, 'r') as file:
            return simplejson.load(file)


class Prompt:

    @staticmethod
    async def prompt(on_reading_fn: Callable[[], Any], on_rewriting_fn: Callable[[], Any], input_msg: str):
        while True:
            try:
                reading_flag = input(input_msg)
                assert reading_flag in ['r', 'w'], 'Only [r/w] are available!'
                if reading_flag == 'r':
                    return on_reading_fn()
                elif reading_flag == 'w':
                    return await on_rewriting_fn()
            except Exception:
                pass
