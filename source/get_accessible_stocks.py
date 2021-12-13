import asyncio
import json
from decimal import Decimal

from aiohttp import ClientSession

from source.components.common.exceptions import ExternalMarketError
from source.components.common.request_handlers import get_stocks, get_orderbook, get_candles, get_figi, request
from source.components.common.request_input_data_makers import make_limit_order_params, make_limit_order_body, headers
from source.components.serializers import Stock
from source.core.config import config
from source.core.extentions import session_provider

from core.extentions import logger
from source.utils.generators import limit_iter


async def make_limit_order_on_purchase(stock: Stock, price: Decimal, lots: int = 1):
    url = config.URL + 'orders/limit-order'
    params = make_limit_order_params(stock.figi)
    body = make_limit_order_body('Buy', price, lots)
    return await request(url, headers, make_limit_order_on_purchase.__name__, method='post', params=params, body=body,
                         ticker=stock.ticker)


async def filter_stocks(stocks: dict[str, Stock]):
    market_limit = 100
    delay = 60
    tasks = [make_limit_order_on_purchase(stock, Decimal('0'), 0) for stock in stocks.values()]
    exception_dict: dict[str, list[str]] = {}
    for ind in limit_iter(tasks, delay, market_limit):
        results = await asyncio.gather(*tasks[ind*market_limit:ind*market_limit+market_limit],
                                       return_exceptions=True)
        logger.info(f'{len(results)=} {results}')
        on_repeat = []
        for result in results:
            if isinstance(result, ExternalMarketError):
                key = str(result.detail)
                if result.code == 429:
                   on_repeat.append(result.ticker)
                else:
                    if key not in exception_dict:
                        exception_dict[key] = []
                    exception_dict[key].append(result.args[2])
            else:
                raise
        tasks += list(map(lambda s: make_limit_order_on_purchase(stocks[s], Decimal('0'), 0), on_repeat))
    with open('exceptions.json', 'w') as file:
        json.dump(exception_dict, file)


async def main():
    async with ClientSession() as session:
        session_provider.append(session)
        stocks = {s.ticker: s for s in (await get_stocks()).payload.instruments}
        await filter_stocks(stocks)


asyncio.run(main())
