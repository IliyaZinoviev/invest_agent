import asyncio

from components.trade.trading import start_trade

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_trade())
