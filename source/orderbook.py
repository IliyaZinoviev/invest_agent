import asyncio
import json

from app.extentions import logger
from clients.tinkoff_invest.api import get_orderbook, get_stocks, client
from clients.tinkoff_invest.client import TinkoffClient
from components.common.exceptions import ExternalMarketError
from components.common.mixins import FilterEnabledStocks
from type_aliases import Ticker
from serializers import Stock, StocksResponse
from utils.generators import limit_iter


async def main():
    res = await get_stocks()
    stocks: list[Stock] = StocksResponse(**res).payload.instruments
    enabled_stocks: dict[Ticker, Stock] = {s.ticker: s for s in FilterEnabledStocks.filter_enabled_stocks(stocks)}
    market_limit = 240
    delay = 60
    tasks = [TinkoffClient.get_orderbook(stock, 1) for stock in enabled_stocks.values()]
    trade_statuses: dict[Ticker, str] = {}
    for ind in limit_iter(tasks, delay, market_limit):
        results = await asyncio.gather(*tasks[ind * market_limit:ind * market_limit + market_limit],
                                       return_exceptions=True)
        logger.info(f'{len(results)=} {results}')
        on_repeat: list[Ticker] = []
        for result in results:
            if not isinstance(result, ExternalMarketError):
                stock, orderbook = result
                trade_statuses[stock.ticker] = orderbook['payload']['tradeStatus']
            else:
                if result.code == 429:
                    on_repeat.append(result.ticker)
                else:
                    logger.info(result)
        tasks += [get_orderbook(enabled_stocks[ticker], 1) for ticker in on_repeat]
        with open('../trade_statuses.json', 'w') as f:
            json.dump(trade_statuses, f)
    await client.aclose()
if __name__ == '__main__':
    asyncio.run(main())
