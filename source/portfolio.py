import asyncio
import json

from clients.tinkoff_invest.api import client
from clients.tinkoff_invest.client import TinkoffClient


async def main():
    portfolio = await TinkoffClient.get_portfolio()
    with open('./portfolio.json', 'w') as f:
        json.dump(portfolio, f, ensure_ascii=False)
    await client.aclose()


if __name__ == '__main__':
    asyncio.run(main())
