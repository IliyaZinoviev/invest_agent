import asyncio

from components.analytics import start_analyze
from components.common.request_handlers import print_accounts
from components.trade import start_trade
from core.extentions import session


async def start_app():
    async with session:
        await print_accounts()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_app())
    loop.run_until_complete(start_analyze())
    loop.run_until_complete(start_trade())
