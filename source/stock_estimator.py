import asyncio

from clients.tinkoff_invest.client import TinkoffClient
from serializers.tinkoff_invest.common import Stock


class StockEstimator:
    async def get_filter_by_price_less_balance(self, stocks: [Stock]):
        pass


async def main():
    estimator = StockEstimator()
    stocks: list[Stock] = (await TinkoffClient.get_stocks()).payload.instruments
    await estimator.get_filter_by_price_less_balance(stocks)


if __name__ == '__main__':
    asyncio.run(main())