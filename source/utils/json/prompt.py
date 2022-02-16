from dataclasses import dataclass
from functools import partial, wraps

from app.config import config
from utils.json.write_json import WriteJson
from utils.prompt import Prompt
from utils.json.read_json import ReadJson


@dataclass
class JsonFileMetaData:
    def __init__(self, name: str):
        self.name: str = name
        self.path: str = f'{config.JSON_PATH}/{name}.json'


class JsonPromptDecorator(Prompt, ReadJson, WriteJson):
    def __init__(self, name: str, serializer=None):
        self._metadata = JsonFileMetaData(name)
        self._input_msg = f'read from {self._metadata.path}; / exec and write result to there; / ' \
                          f'exec without saving? [rwi]\n>>>'
        self._serializer = serializer

    async def _prompt(self, fn):
        on_reading_fn = partial(self.read_json, self._metadata.path, serializer=self._serializer)
        on_writing_fn = partial(self._write_fn_res_to_json, self._metadata.path, fn)
        return await self.prompt(on_reading_fn, on_writing_fn, fn, self._input_msg)

    def __call__(self, fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            bind_fn = partial(fn, *args, **kwargs)
            return await self._prompt(bind_fn)
        return wrapper
