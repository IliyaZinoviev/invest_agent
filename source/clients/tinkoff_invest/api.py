from collections.abc import Callable, Awaitable
from typing import TypeVar

from httpx import AsyncClient, Response

from clients.tinkoff_invest.api_call import TinkoffInvestApiCall
from serializers.tinkoff_invest.response import TinkoffInvestResp, Error
from app.config import config
from clients.base import Middleware
from clients.middlewares import get_json

headers = {'Authorization': f'Bearer {config.TOKEN}'}
params = [('brokerAccountId', config.BROKER_ACC_ID)]


client = AsyncClient(
    base_url=config.BASE_URL,
    headers=headers,
    params=params,
)


class ExternalServiceError(Exception):
    def __init__(self, error: Error | None, code: int):
        if error:
            self.msg = error.code
            self.detail = error.message
        else:
            self.msg = None
            self.detail = None
        self.code = code


T = TypeVar('T')


async def raise_exc(data: T, handler: Callable[[T], Awaitable[Response]]) -> Response:
    res = await handler(data)
    if res.status_code in [500, 503, 401, 429, 403]:
        try:
            error = Error(**TinkoffInvestResp(**res.json()).payload)
        except Exception:
            raise ExternalServiceError(None, res.status_code)
        else:
            raise ExternalServiceError(error, res.status_code)
    return res

middlewares: Middleware = (get_json, raise_exc)

get_orderbook = TinkoffInvestApiCall(client, 'market/orderbook', middleware=middlewares)

get_candles = TinkoffInvestApiCall(client, 'market/candles', middleware=middlewares)

get_instrument_by_ticker = TinkoffInvestApiCall(client, 'market/search/by-ticker', middleware=middlewares)

get_stocks = TinkoffInvestApiCall(client, 'market/stocks', middleware=middlewares)

get_portfolio = TinkoffInvestApiCall(client, 'portfolio', middleware=middlewares)

get_currencies = TinkoffInvestApiCall(client, 'portfolio/currencies', middleware=middlewares)

get_orders = TinkoffInvestApiCall(client, 'orders', middleware=middlewares)

create_limit_order = TinkoffInvestApiCall(client, 'orders/limit-order', method='POST', middleware=middlewares)

cancel_order = TinkoffInvestApiCall(client, 'orders/cancel', method='POST', middleware=middlewares)

get_operations = TinkoffInvestApiCall(client, 'operations', middleware=middlewares)
