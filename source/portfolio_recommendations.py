import asyncio
from typing import TypeAlias

from aiohttp import ClientSession

from source.components.common.enums import CurrencyEnum
from source.components.common.mixins import FilterEnabledStocks, GetStockDict, GetPortfolioRecommendations
from source.components.common.request_handlers import get_stocks
from source.components.common.type_aliases import Ticker
from source.components.serializers import Stock
from source.core.extentions import session_provider


class PortfolioRecommendations(FilterEnabledStocks, GetStockDict, GetPortfolioRecommendations):

    @classmethod
    async def main(cls):
        async with ClientSession() as session:
            session_provider.append(session)
            stocks: list[Stock] = (await get_stocks()).payload.instruments
            enabled_stocks: dict[Ticker, Stock] = {s.ticker: s for s in cls.filter_enabled_stocks(stocks)}
            stock_dict: dict[CurrencyEnum, list[tuple]] = await cls.get_stock_dict(enabled_stocks)
            cls.get_portfilio_recommendations(stock_dict, [250000, 1600], ['RUB', 'USD'])


if __name__ == '__main__':
    asyncio.run(PortfolioRecommendations.main())
