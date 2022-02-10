import asyncio

from aiohttp import ClientSession
from components.analytics import start_analyze
from components.common.request_handlers import print_accounts
from components.trade import start_trade
from app.extentions import session_provider


async def start_app():
    session = ClientSession()
    session_provider.append(session)
    async with session:
        await print_accounts()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_analyze())
    loop.run_until_complete(start_trade())
