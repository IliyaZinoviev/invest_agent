import asyncio

from aiohttp import ClientSession

from source.components.common.enums import CurrencyEnum
from source.components.common.mixins import (
    FilterEnabledStocks, GetPortfolioRecommendations, GetStockDict, StockDictItem, PortfolioRecommendationData)
from components.common.enums import AccEnum
from source.components.common.request_handlers import get_stocks
from source.components.common.type_aliases import Ticker
from source.components.serializers import Stock
from source.core.extentions import session_provider


class PortfolioRecommendations(FilterEnabledStocks, GetStockDict, GetPortfolioRecommendations):

    @classmethod
    async def get_portfolio_recommendations(cls, input_data: [PortfolioRecommendationData]):
        async with ClientSession() as session:
            session_provider.append(session)
            stocks: list[Stock] = (await get_stocks()).payload.instruments
            enabled_stocks: dict[Ticker, Stock] = {s.ticker: s for s in cls.filter_enabled_stocks(stocks)}
            stock_dict: dict[CurrencyEnum, list[StockDictItem]] = await cls.get_stock_dict(enabled_stocks)
            portfolio_reccomendation_data: [PortfolioRecommendationData] = [
                PortfolioRecommendationData(250000, AccEnum.IIS, CurrencyEnum.RUB),
                PortfolioRecommendationData(3250, AccEnum.IIS, CurrencyEnum.USD),
                PortfolioRecommendationData(1500, AccEnum.BROKER, CurrencyEnum.USD),
            ]
            await cls.get_portfilio_recommendations(stock_dict, *portfolio_reccomendation_data)


if __name__ == '__main__':
    asyncio.run(PortfolioRecommendations.get_portfolio_recommendations())
