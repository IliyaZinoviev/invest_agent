import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, Union

from components.common.enums import AccEnum
from components.common.exceptions import ExternalMarketError
from pydantic import BaseModel

from source.components.common.enums import CurrencyEnum
from source.components.common.request_handlers import get_orderbook
from source.components.common.type_aliases import Asset, Ticker
from source.components.serializers import OrderbookResponse, Stock
from source.core.extentions import logger
from source.utils.generators import limit_iter
from source.utils.utils import JsonPromptDecorator, ReadJson


@dataclass
class JsonFileMetaData:
    def __init__(self, name: str):
        self.name: str = name
        self.path: str = f'../{name}.json'


class StockDictItem(BaseModel):
    ticker: str
    norm_price: Decimal  # price * lot


class StockDict(BaseModel):
    __root__: dict[CurrencyEnum, list[StockDictItem]]


class PortfolioItem(StockDictItem):
    count: int
    invested_funds: Decimal
    share: Decimal


class Portfolio(BaseModel):
    __root__: dict[str, list[PortfolioItem]]
    asset: Decimal


@dataclass
class PortfolioRecommendationData:
    asset: Asset
    acc: AccEnum
    currency: CurrencyEnum


class GetPortfolioRecommendations:
    file_meta_data = JsonFileMetaData('portfolio_recommendations')

    @classmethod
    @JsonPromptDecorator(file_meta_data.path, f'read {file_meta_data.name} or rewrite? [rw]', Portfolio)
    def get_portfilio_recommendations(
            cls,
            stocks_dict: dict[CurrencyEnum, [StockDictItem]],
            *portfolio_recommendation_data_list: PortfolioRecommendationData,
    ):
        result: dict[str, [PortfolioItem]] = {}
        for data in portfolio_recommendation_data_list:
            result[f'({data.acc}, {data.currency})'] = cls._get_portfolio_recommendation(
                data.asset, stocks_dict[data.currency])
        return result

    @classmethod
    def _get_portfolio_recommendation(cls, asset: int, stocks: [StockDictItem]) -> [PortfolioItem]:
        sorted_stocks = sorted(stocks, key=lambda s: s.norm_price)
        ind = cls._binary_search(sorted_stocks, asset)
        portfolio_recommendation, balance, do_next_search = cls._get_portfolio_recommendation_(
            asset, sorted_stocks, ind)
        result = (portfolio_recommendation, balance, do_next_search)
        ind += 1
        while do_next_search and ind < len(sorted_stocks):
            result = (portfolio_recommendation, balance, do_next_search)
            portfolio_recommendation, balance, do_next_search = cls._get_portfolio_recommendation_(
                asset, sorted_stocks, ind)
            ind += 1
        return result[0]

    @staticmethod
    def _get_portfolio_recommendation_(
            asset: Asset, sorted_stocks: list[StockDictItem], ind: int) -> (PortfolioItem, Asset, bool):
        initial_asset: Asset = asset
        one_percent_part_of_initial_asset: Decimal = Decimal(initial_asset/100)
        max_val: Decimal = sorted_stocks[ind].norm_price
        portfolio_recommendation = [PortfolioItem(
            ticker=sorted_stocks[ind].ticker,
            norm_price=sorted_stocks[ind].norm_price,
            count=1,
            invested_funds=sorted_stocks[ind].norm_price,
            share=sorted_stocks[ind].norm_price/one_percent_part_of_initial_asset,
        )]
        asset -= max_val + (max_val / 100 * Decimal('0.05'))
        for stock in sorted_stocks[:ind][::-1]:
            n = max_val // stock.norm_price
            updated_asset: Asset = asset - (stock.norm_price + (stock.norm_price / 100 * Decimal('0.05'))) * n
            if updated_asset < 0:
                return portfolio_recommendation, asset, updated_asset > 0
            invested_funds: Decimal = stock.norm_price * n
            portfolio_recommendation.append(PortfolioItem(
                ticker=stock.ticker,
                norm_price=stock.norm_price,
                count=n,
                invested_funds=invested_funds,
                share=invested_funds/one_percent_part_of_initial_asset,
            ))
            asset = updated_asset
        return portfolio_recommendation, asset, asset > 0

    @staticmethod
    def _binary_search(a: list[StockDictItem], x, lo=0, hi=None) -> int:
        if hi is None:
            hi = len(a)
        mid = None
        while lo < hi:
            mid = (lo + hi) // 2
            midval = a[mid]
            n = x // midval.norm_price
            if len(a[:mid + 1]) < n:
                lo = mid + 1
            elif len(a[:mid + 1]) > n:
                hi = mid
            else:
                return mid
        return mid


class GetStockDict:
    file_meta_data = JsonFileMetaData('stocks_dict')

    @staticmethod
    @JsonPromptDecorator(file_meta_data.path, f'read {file_meta_data.name} or rewrite? [rw]', StockDict)
    async def get_stock_dict(stocks: dict[Ticker, Stock]) -> dict[CurrencyEnum, list[StockDictItem]]:
        market_limit = 240
        delay = 60
        stocks_dict: dict[CurrencyEnum, list[StockDictItem]] = {}
        tasks = [get_orderbook(stock, 1) for stock in stocks.values()]
        orderbook_results: list[Union[OrderbookResponse, ExternalMarketError]] = []
        for ind in limit_iter(tasks, delay, market_limit):
            results = await asyncio.gather(*tasks[ind * market_limit:ind * market_limit + market_limit],
                                           return_exceptions=True)
            orderbook_results += results
            logger.info(f'{len(results)=} {results}')
            on_repeat: list[Ticker] = []
            for result in results:
                if not isinstance(result, ExternalMarketError):
                    orderbook, stock = result
                    if stock.currency not in stocks_dict:
                        stocks_dict[stock.currency] = []
                    norm_price = Decimal(str(orderbook.payload.lastPrice)) * stock.lot
                    item: StockDictItem = StockDictItem(ticker=stock.ticker, norm_price=norm_price)
                    stocks_dict[stock.currency].append(item)
                else:
                    if result.code == 429:
                        on_repeat.append(result.ticker)
                    else:
                        logger.info(result)
            tasks += [get_orderbook(stocks[ticker], 1) for ticker in on_repeat]
        return stocks_dict


class FilterEnabledStocks(ReadJson):

    @classmethod
    def filter_enabled_stocks(cls, stocks: list[Stock]) -> Iterator[Stock]:
        tickers = cls.read_json('../disabled_stocks.json')
        return filter(lambda s: s.ticker not in tickers, stocks)
