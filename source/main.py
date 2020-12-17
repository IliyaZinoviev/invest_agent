import asyncio
import logging

from source.monitoring_agent import start_monitoring_agent

logging.basicConfig(level=logging.INFO)


async def main():
    await start_monitoring_agent()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
