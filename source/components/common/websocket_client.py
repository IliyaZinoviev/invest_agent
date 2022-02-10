import asyncio
import json
from typing import Callable, Sequence

import websockets
from aiohttp import ClientSession

from source.components.common.request_handlers import get_figi
from source.app.config import config
from source.app.extentions import session_provider


async def consumer_handler(websocket):
    async for message in websocket:
        print(f"<<< {message}")


async def subscribe_on_event(websocket, event: dict[str, str]):
    await websocket.send(json.dumps(event))


async def subscribe_on_candles(websocket, ticker: str):
    await subscribe_on_event(websocket, {
        "event": "candle:subscribe",
        "figi": await get_figi(ticker),
        "interval": "1min",
    })


async def subscribe_on_orderbook(websocket, ticker: str):
    await subscribe_on_event(websocket, {
        "event": "orderbook:subscribe",
        "figi": await get_figi(ticker),
        "depth": 20,
    })


async def get_connection(ticker, subscribe_fn):
    async with websockets.connect('wss://api-invest.tinkoff.ru/openapi/md/v1/md-openapi/ws',
                                  extra_headers={'Authorization': "Bearer " + config.TOKEN}) as websocket:
        await subscribe_fn(websocket, ticker)
        await consumer_handler(websocket)


async def subscribe_connections(connections_data: Sequence[tuple[str, Callable]]):
    while True:
        tasks = [asyncio.ensure_future(get_connection(ticker, subscribe_fn))
                 for ticker, subscribe_fn in connections_data]
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


async def main():
    async with ClientSession() as session:
        session_provider.append(session)
        await subscribe_connections([('MNK', subscribe_on_candles), ('MNK', subscribe_on_orderbook)])
        session_provider.pop()


if __name__ == '__main__':
    asyncio.run(main())
