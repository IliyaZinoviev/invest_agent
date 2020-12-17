import asyncio
import logging

from source.analytics import get_analytics
from source.common import get_figi
from source.config import TICKERS
from source.extentions import session
from source.monitoring_agent import start_monitoring_agent

logging.basicConfig(level=logging.INFO)


async def main():
    tasks = [get_figi(ticker)
             for ticker in TICKERS]
    figies = {ticker: figi for ticker, figi in await asyncio.gather(*tasks)}
    async with session:
        await get_analytics(figies)
        await start_monitoring_agent(figies)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
