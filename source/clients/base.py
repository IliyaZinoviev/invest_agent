from functools import reduce
from typing import TypeAlias, Optional, Callable, Any

from httpx import AsyncClient, Response

Middleware: TypeAlias = Optional[tuple[Callable[[Any, Callable], Any], ...]]


def strip_none(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


def handler_factory(handler: Callable, middleware: Callable[[Any, Callable], Any]):
    async def handle(data):
        return await middleware(data, handler)

    return handle


class ApiCall:
    def __init__(self, client: AsyncClient, path: str, *, method: str = 'GET', middleware: Middleware = None):
        self._client = client
        self._path = path
        self._method = method
        self._handler = reduce(handler_factory, (middleware or [])[::-1], self._call)

    async def _call(self, parameters: dict) -> Response:
        path_params = parameters.pop('path_params', {})
        path = self._path.format(**path_params)
        headers = (dict(self._client.headers) or {}) | (parameters.get('headers') or {})

        if headers:
            parameters['headers'] = headers

        return await self._client.request(self._method, path, **parameters)

    async def __call__(self, data=None, json=None, params=None, path_params=None, headers=None, **kwargs) -> Response:
        return await self._handler(
            strip_none(
                data=data, json=json, params=params, path_params=path_params, headers=headers, **kwargs
            )
        )
