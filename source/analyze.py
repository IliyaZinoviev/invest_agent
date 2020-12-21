import asyncio

from components.analytics import start_analyze

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_analyze())
