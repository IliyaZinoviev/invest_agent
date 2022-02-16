from asyncio import sleep, Semaphore
from datetime import datetime
from time import monotonic

from httpx import Response, AsyncClient

from app.extentions import logger
from clients.base import ApiCall, Middleware


class Limiter:
    def __init__(self, value=1, delay: float = 60):
        self._semaphore = Semaphore(value)
        self._delay = delay
        self._val = value
        self._max_val = value
        self._start = None
        self._lock = False

    async def __aenter__(self):
        await self._semaphore.acquire()
        if self.is_expired():
            self._reset()
        if self.is_first():
            self._start = monotonic()
        return None

    async def __aexit__(self, exc_type, exc, tb):
        if self._semaphore.locked() and not self._lock:
            print('print', datetime.now())
            self._lock = True
            diff = monotonic() - self._start
            logger.info(self._delay - diff)
            await sleep(self._delay - diff)
            self._release()
        pass

    def _release(self):
        self._start = None
        self._lock = False
        for _ in range(self._max_val):
            self._semaphore.release()

    def _reset(self):
        self._start = None
        self._lock = False
        val = self._max_val - self._semaphore._value
        for _ in range(val):
            self._semaphore.release()

    def is_first(self) -> bool:
        return not self._start

    def is_expired(self) -> bool:
        if self._start:
            return self._delay < monotonic() - self._start
        return False


class TinkoffInvestApiCall(ApiCall):
    _limiter_map = {
        'sandbox': Limiter(120),
        'portfolio': Limiter(120),
        'market': Limiter(240),
        'orders/limit-order': Limiter(100, 60),
        'orders/market-order': Limiter(100),
        'orders/cancel': Limiter(50),
        'orders': Limiter(100),
        'operations': Limiter(120),
    }
    _start = None
    _end = None

    def __init__(self, client: AsyncClient, path: str, *, method: str = 'GET', middleware: Middleware = None):
        super().__init__(client, path, method=method, middleware=middleware)
        self._limiter = self.get_limiter(path)

    async def _call(self, parameters: dict) -> Response:
        if not self._limiter:
            res = await super()._call(parameters)
            return res
        async with self._limiter:
            res = await super()._call(parameters)
            return res

    @classmethod
    def get_limiter(cls, path: str):
        key = cls.get_key(path)
        return cls._limiter_map.get(key, None)

    @classmethod
    def get_key(cls, path):
        if path[0] == '/':
            path = path[1:]
        if path.startswith('orders'):
            return path
        return path.split('/', maxsplit=1)[0]
