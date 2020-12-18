import asyncio

from source.analytics import get_analytics
from source.common import get_figi
from source.config import TICKERS
from source.extentions import session
from source.monitoring_agent import start_monitoring_agent, get_daily_result, save_daily_result


async def main():
    async with session:
        tasks = [get_figi(ticker) for ticker in TICKERS]
        figies = {ticker: figi for ticker, figi in await asyncio.gather(*tasks)}
        sorted_stocks = await get_analytics(figies)
        daily_result_data = await start_monitoring_agent(sorted_stocks)
    daily_result = get_daily_result(daily_result_data)
    save_daily_result(daily_result)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
