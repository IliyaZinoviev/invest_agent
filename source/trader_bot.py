import asyncio
from decimal import Decimal
from typing import NamedTuple

from app.config import config
from components.common.enums import OperationEnum, TariffEnum
from type_aliases import Ticker
from price_executor import PriceExecutor
from serializers.tinkoff_invest.request import LimitOrderReq, CancelOrderReq
from serializers.tinkoff_invest.common import Order, Stock, OrderBook
from clients.tinkoff_invest.api import client
from clients.tinkoff_invest.client import TinkoffClient
from utils.generators import limit_iter


class FeeParams(NamedTuple):
    percentage: Decimal
    price_limit: Decimal


class TraderAgent:

    tariff = config.TARIFF

    @classmethod
    async def _has_in_portfolio(cls, ticker: Ticker):
        portfolio = await TinkoffClient.get_portfolio()
        return portfolio.get(ticker)

    @classmethod
    async def _has_balance_for_purchase(cls, stock: Stock, orderbook: OrderBook) -> bool:
        currencies = await TinkoffClient.get_currencies()
        currency = currencies.get(stock.currency)
        blocked = currency.blocked if currency.blocked else 0
        res = currency.balance - blocked > orderbook.limit_down
        return res

    @classmethod
    async def _has_active_order(cls):
        res = await TinkoffClient.get_active_orders()

    @classmethod
    async def _init_order_ids(cls, stock: Stock) -> dict[Ticker, [str]]:
        orders: [Order] = sorted(await TinkoffClient.get_active_orders(), key=lambda x: x.price)
        order_ids: dict[Ticker, [str]] = {}
        for order in orders:
            if order.figi == stock.figi:
                if stock.ticker not in order_ids:
                    order_ids[stock.ticker] = []
                order_ids[stock.ticker].append(order.id_)
        return order_ids

    @classmethod
    async def _cancel_all_active_orders(cls):
        orders = await TinkoffClient.get_active_orders()
        cancel_limit = 50
        for i in limit_iter(orders, 90, cancel_limit):
            tasks = [TinkoffClient.cancel_order(CancelOrderReq(**order.dict()))
                     for order in orders[i * cancel_limit:(i + 1) * cancel_limit]]
            await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    async def _get_average_price(cls, stock: Stock):
        price_executor = PriceExecutor(stock)
        return price_executor()

    @classmethod
    def _get_fee(cls, price: Decimal) -> Decimal:
        fee_params_map = {
            TariffEnum.TRADER: FeeParams(Decimal('0.0004'), Decimal('36.11')),
            TariffEnum.INVESTOR: FeeParams(Decimal('0.003'), Decimal('4.81')),
        }
        fee_params: FeeParams = fee_params_map[cls.tariff]
        if price <= fee_params.price_limit:
            res = Decimal('0.01')
        else:
            res = round(price * fee_params.percentage, 2)
        return res

    @classmethod
    async def _get_plan(cls, avg_price: Decimal, lots: int, balance: Decimal, curr_price: Decimal) -> Decimal:
        extra_lots = balance // curr_price
        return (avg_price * lots + extra_lots * curr_price) / (lots + extra_lots)

    @classmethod
    async def __call__(cls):
        ticker = 'SLDB'
        stock: Stock = await TinkoffClient.get_instrument_by_ticker(ticker)
        # order_ids: dict[Ticker, [str]] = await cls._init_order_ids(stock)
        try:

            # while True:
            #     orderbook: OrderBook = await TinkoffClient.get_orderbook(stock, 20)
            #     if position := await cls._has_in_portfolio(ticker):
            #         pass
            #
            #     else:
            #         if cls._has_balance_for_purchase(stock, orderbook):
            #             pass
            limit_order_limit = 100
            delay = 60
            orders = await TinkoffClient.get_active_orders()
            limit_order_req = LimitOrderReq(
                figi=stock.figi,
                lots=1,
                price=1,
                operation=OperationEnum.BUY,
            )
            order_tasks = [TinkoffClient.get_active_orders() for _ in range(100)]
            tasks = [TinkoffClient.create_limit_order(limit_order_req) for _ in range(100)]
            # orders = await asyncio.gather(*(order_tasks + tasks + cancel_tasks), return_exceptions=True)
            # await cls._cancel_all_active_orders()

        except Exception:
            raise
        finally:
            await client.aclose()


if __name__ == '__main__':
    agent = TraderAgent()
    asyncio.run(agent())
