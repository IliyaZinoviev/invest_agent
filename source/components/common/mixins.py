import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Union, Iterator, NamedTuple

from source.components.common.enums import CurrencyEnum
from source.components.common.request_handlers import get_orderbook
from source.components.common.type_aliases import Ticker, Asset
from source.components.serializers import OrderbookResponse, Stock

from source.core.extentions import logger
from source.utils.generators import limit_iter
from source.utils.utils import JsonPromptDecorator, ReadJson


@dataclass
class JsonFileMetaData:
    def __init__(self, name: str):
        self.name: str = name
        self.path: str = f'../{name}.json'


@dataclass
class StockDictItem(NamedTuple):
    ticker: str
    norm_price: Decimal  # price * lot


@dataclass
class Portfolio(StockDictItem):
    count: int
    invested_funds: Decimal
    share: Decimal


class GetPortfolioRecommendations:
    file_meta_data = JsonFileMetaData('portfolio_recommendations')

    @classmethod
    @JsonPromptDecorator(file_meta_data.path, f'read {file_meta_data.name} or rewrite? [rw]')
    def get_portfilio_recommendations(
            cls,
            stocks_dict: dict[CurrencyEnum, list[StockDictItem]],
            asset_list: list[int],
            currencies: list[CurrencyEnum],
    ):
        result: dict[CurrencyEnum, Portfolio] = {}
        for asset, currency in zip(asset_list, currencies):
            result[currency] = cls._get_portfolio_recommendation(asset, stocks_dict[currency])
        return result

    @classmethod
    def _get_portfolio_recommendation(cls, asset: int, stocks: list[StockDictItem]) -> Portfolio:
        sorted_stocks = sorted(stocks, key=lambda s: s[1])
        ind = cls._binary_search(sorted_stocks, asset)
        portfolio_recommendation, temp_asset = cls._get_portfolio_recommendation_(asset, sorted_stocks, ind)
        result = (portfolio_recommendation, temp_asset)
        while temp_asset > 0:
            result = (portfolio_recommendation, temp_asset)
            ind += 1
            portfolio_recommendation, temp_asset = cls._get_portfolio_recommendation_(asset, sorted_stocks, ind)
        return result

    @staticmethod
    def _get_portfolio_recommendation_(
            asset: int, sorted_stocks: list[StockDictItem], ind: int) -> tuple[Portfolio, Asset]:
        max_val: Decimal = sorted_stocks[ind].norm_price
        portfolio_recommendation = [Portfolio(
            sorted_stocks[ind].ticker, sorted_stocks[ind].norm_price, 1, sorted_stocks[ind].norm_price, Decimal(0)
        )]
        asset -= max_val + (max_val / 100 * Decimal('0.05'))
        for stock in sorted_stocks[:ind][::-1]:
            n = max_val // stock[1]
            asset -= (stock[1] + (stock[1] / 100 * Decimal('0.05'))) * n
            if asset < 0:
                return portfolio_recommendation, asset
            portfolio_recommendation.append((stock[0], stock[1], n, stock[1] * n))
        return portfolio_recommendation, asset

    @staticmethod
    def _binary_search(a, x, lo=0, hi=None) -> int:
        if hi is None:
            hi = len(a)
        mid = None
        while lo < hi:
            mid = (lo + hi) // 2
            midval = a[mid]
            n = x // midval[1]
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
    @JsonPromptDecorator(file_meta_data.path, f'read {file_meta_data.name} or rewrite? [rw]')
    async def get_stock_dict(stocks: dict[Ticker, Stock]) -> dict[CurrencyEnum, list[StockDictItem]]:
        market_limit = 240
        delay = 60
        stocks_dict: dict[CurrencyEnum, list[StockDictItem]] = {}
        tasks = [get_orderbook(stock, 1) for stock in stocks.values()]
        orderbook_results: list[Union[OrderbookResponse, Exception]] = []
        for ind in limit_iter(tasks, delay, market_limit):
            results = await asyncio.gather(*tasks[ind * market_limit:ind * market_limit + market_limit],
                                           return_exceptions=True)
            orderbook_results += results
            logger.info(f'{len(results)=} {results}')
            on_repeat: list[Ticker] = []
            for result in results:
                if not isinstance(result, Exception):
                    orderbook, stock = result
                    if stock.currency not in stocks_dict:
                        stocks_dict[stock.currency] = []
                    norm_price = Decimal(str(orderbook.payload.lastPrice)) * stock.lot
                    item: StockDictItem = StockDictItem(stock.ticker, norm_price)
                    stocks_dict[stock.currency].append(item)
                else:
                    if result.args[3] == 429:
                        on_repeat.append(result.args[2])
                    else:
                        logger.info(result)
            tasks += list(map(lambda s: get_orderbook(stocks[s], 1), on_repeat))
        return stocks_dict


class FilterEnabledStocks(ReadJson):

    @classmethod
    def filter_enabled_stocks(cls, stocks: list[Stock]) -> Iterator[Stock]:
        tickers = cls.read_json('../disabled_stocks.json')
        return filter(lambda s: s.ticker not in tickers, stocks)
