from typing import Callable, Optional, NamedTuple, Awaitable

from httpx import AsyncClient

from clients.tinkoff_invest.api_call import TinkoffInvestApiCall
from serializers.tinkoff_invest_serializers import ErrorResp
from serializers.tinkoff_invest.response import TinkoffInvestResp, Error
from source.app.config import config
from source.clients.base import Middleware
from source.clients.middlewares import get_json
from serializers.tinkoff_invest.common import Stock

headers = {'Authorization': f'Bearer {config.TOKEN}'}
params = [('brokerAccountId', config.BROKER_ACC_ID)]


client = AsyncClient(
    base_url=config.BASE_URL,
    headers=headers,
    params=params,
)


class ExternalServiceError(Exception):
    def __init__(self, error: Optional[Error], code: int):
        if error:
            self.msg = error.code
            self.detail = error.message
        else:
            self.msg = None
            self.detail = None
        self.code = code


async def raise_exc(data: dict, handler: Callable) -> dict:
    try:
        res = await handler(data)
        if res.status_code in [500, 503, 401, 429, 403]:
            try:
                error = Error(**TinkoffInvestResp(**res.json()).payload)
            except Exception:
                raise ExternalServiceError(None, res.status_code)
            raise ExternalServiceError(error, res.status_code)
        return res
    except Exception:
        raise

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
