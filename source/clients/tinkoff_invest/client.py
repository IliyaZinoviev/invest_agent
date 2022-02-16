from clients.tinkoff_invest.api import get_orderbook, get_candles, get_portfolio, get_currencies, \
    get_orders, get_instrument_by_ticker, get_stocks, create_limit_order, cancel_order, get_operations
from components.common.enums import CurrencyEnum
from type_aliases import Ticker
from serializers.tinkoff_invest.request import OperationsReq, LimitOrderReq, CancelOrderReq, CandlesReq
from serializers.tinkoff_invest.response import TinkoffInvestResp, LimitOrder
from serializers.tinkoff_invest.common import Operations, Position, Portfolio, Currency, Currencies, Candle, Candles, \
    Order, Stock, Stocks, OrderBook


class TinkoffClient:

    @staticmethod
    async def get_orderbook(stock: Stock, depth: int) -> OrderBook:
        res = await get_orderbook(params={'figi': stock.figi, 'depth': depth})
        return OrderBook(**TinkoffInvestResp(**res).payload)

    @staticmethod
    async def get_candles(input_data: CandlesReq) -> [Candle]:
        res = await get_candles(params=input_data.dict())
        return Candles(**TinkoffInvestResp(**res).payload).candles

    @staticmethod
    async def get_portfolio() -> dict[Ticker, Position]:
        res = await get_portfolio()
        return {position.ticker: position for position in Portfolio(**TinkoffInvestResp(**res).payload).positions}

    @staticmethod
    async def get_currencies() -> dict[CurrencyEnum, Currency]:
        res = await get_currencies()
        return {item.currency: item for item in Currencies(**TinkoffInvestResp(**res).payload).currencies}

    @staticmethod
    async def get_active_orders() -> [Order]:
        res = await get_orders()
        return TinkoffInvestResp(**res).payload

    @staticmethod
    async def get_instrument_by_ticker(ticker: Ticker) -> Stock:
        res = await get_instrument_by_ticker(params={'ticker': ticker})
        return Stocks(**TinkoffInvestResp(**res).payload).instruments[0]

    @staticmethod
    async def get_stocks() -> [Stock]:
        res = await get_stocks()
        return Stocks(**TinkoffInvestResp(**res).payload).instruments

    @staticmethod
    async def create_limit_order(input_data: LimitOrderReq) -> LimitOrder:
        res = await create_limit_order(
            params=input_data.dict(include={'figi'}),
            json=input_data.dict(include={'lots', 'price', 'operation'}),
        )
        return LimitOrder(**TinkoffInvestResp(**res).payload)

    @staticmethod
    async def cancel_order(input_data: CancelOrderReq):
        res = await cancel_order(params=input_data.dict())
        return res

    @staticmethod
    async def get_operations(input_data: OperationsReq) -> Operations:
        res = await get_operations(params=input_data.dict())
        return Operations(**TinkoffInvestResp(**res).payload)
