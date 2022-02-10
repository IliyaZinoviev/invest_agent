import asyncio
from datetime import datetime, timedelta, timezone

from components.common.enums import IntervalEnum
from components.common.mixins import FilterEnabledStocks
from type_aliases import Ticker
from serializers.tinkoff_invest.request import CandlesReq
from serializers.tinkoff_invest.common import Stock
from clients.tinkoff_invest.api import client
from clients.tinkoff_invest.client import TinkoffClient


async def main():
    stocks: list[Stock] = await TinkoffClient.get_stocks()
    enabled_stocks: dict[Ticker, Stock] = {s.ticker: s for s in FilterEnabledStocks.filter_enabled_stocks(stocks)}
    candles = await TinkoffClient.get_candles(CandlesReq(
        figi=enabled_stocks['YNDX'].figi,
        to=datetime.now(tz=timezone(timedelta(hours=3))).isoformat(),
        from_=(datetime.now(tz=timezone(timedelta(hours=3))) - timedelta(days=7)).isoformat(),
        interval=IntervalEnum.DAY,
    ))
    await client.aclose()


if __name__ == '__main__':
    asyncio.run(main())
