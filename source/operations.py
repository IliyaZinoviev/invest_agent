import asyncio
from datetime import datetime, timezone, timedelta

from clients.tinkoff_invest.api import client
from clients.tinkoff_invest.client import TinkoffClient
from serializers.tinkoff_invest.request import OperationsReq
from serializers.tinkoff_invest.common import Stock


async def main():
    stock: Stock = await TinkoffClient.get_instrument_by_ticker('SEDG')
    now_dt = datetime.now(tz=timezone(timedelta(hours=3)))
    await TinkoffClient.get_operations(
        OperationsReq(to=now_dt.isoformat(),
                      from_=(now_dt - timedelta(days=5)).isoformat(),
                      figi=stock.figi)
    )
    await client.aclose()


if __name__ == '__main__':
    asyncio.run(main())
