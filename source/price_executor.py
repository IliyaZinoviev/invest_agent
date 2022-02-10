import asyncio
from datetime import datetime, timedelta, timezone, date, time

from clients.tinkoff_invest.api import client
from clients.tinkoff_invest.client import TinkoffClient
from components.common.enums import IntervalEnum
from serializers.tinkoff_invest.request import CandlesReq
from serializers.tinkoff_invest.common import Candle, Stock


class PriceExecutor:
    timedelta_map = {
        IntervalEnum.D1MIN: timedelta(minutes=2),
        IntervalEnum.D2MIN: timedelta(minutes=4),
        IntervalEnum.D3MIN: timedelta(minutes=6),
        IntervalEnum.D5MIN: timedelta(minutes=10),
        IntervalEnum.D10MIN: timedelta(minutes=20),
        IntervalEnum.D15MIN: timedelta(minutes=30),
        IntervalEnum.D30MIN: timedelta(hours=1),
        IntervalEnum.HOUR: timedelta(hours=2),
        IntervalEnum.DAY: timedelta(days=2),
        IntervalEnum.WEEK: timedelta(weeks=2),
        IntervalEnum.MONTH: timedelta(weeks=8),
    }

    def __init__(self, stock):
        self.stock: Stock = stock

    async def get_min_price(self):
        interval = IntervalEnum.MONTH
        candles: [Candle] = await TinkoffClient.get_candles(CandlesReq(
            figi=self.stock.figi,
            to=datetime.combine(date.today()+timedelta(days=1), time(), tzinfo=timezone(timedelta(hours=3))).isoformat(),
            from_=datetime.combine(date.today() - timedelta(weeks=520), time(), tzinfo=timezone(timedelta(hours=3))).isoformat(),
            interval=interval,
        ))

    async def get_average_percentages(self):
        interval = IntervalEnum.MONTH
        candles: [Candle] = await TinkoffClient.get_candles(CandlesReq(
            figi=self.stock.figi,
            to=datetime.combine(date.today()+timedelta(days=1), time(), tzinfo=timezone(timedelta(hours=3))).isoformat(),
            from_=datetime.combine(date.today() - timedelta(weeks=520), time(), tzinfo=timezone(timedelta(hours=3))).isoformat(),
            interval=interval,
        ))
        # sum_percantage = 0
        # for curr_candle, next_candle in zip(candles, candles[1:]):
        #     next_candle.h, curr_candle.l
        #     percentage = abs(100 - (100 * candle.l / candle.h))
        #     sum_percantage += percentage
        # average = sum_percantage / length
        # print(average)

    async def __call__(self):
        await self.get_average_price()
        # res = []
        # print()
        # for interval in IntervalEnum:
        #     candles: [Candle] = await TinkoffClient.get_candles(CandlesReq(
        #         figi=self.stock.figi,
        #         to=datetime.now(tz=timezone(timedelta(hours=3))).isoformat(),
        #         from_=(datetime.now(tz=timezone(timedelta(hours=3))) - self.timedelta_map[interval]).isoformat(),
        #         interval=interval,
        #     ))
        #     candle = candles
        #     print(candle)
        #     # percentage = 100 - (100 * candle.l / candle.h)
        #     # print(interval, percentage, sep=', ')
        #     # print(candle.h, candle.l, sep=', ')


async def main():
    ticker = 'YNDX'
    stock: Stock = await TinkoffClient.get_instrument_by_ticker(ticker)
    price_executor = PriceExecutor(stock)
    await price_executor()
    await client.aclose()

if __name__ == '__main__':
    asyncio.run(main())
