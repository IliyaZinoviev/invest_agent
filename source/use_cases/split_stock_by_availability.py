import asyncio
from decimal import Decimal
from functools import partial
from pprint import pprint
from typing import NamedTuple, Awaitable

from app.config import config
from app.extentions import logger
from clients.tinkoff_invest.api import client, ExternalServiceError
from clients.tinkoff_invest.client import TinkoffClient
from components.common.enums import OperationEnum
from helpers.policies import TimedEventLoopPolicy, print_timing
from helpers.sound_notifier import sound_notifier
from serializers.tinkoff_invest.request import LimitOrderReq
from serializers.tinkoff_invest.common import Stock
from utils.utils import timeit
from utils.json.prompt import JsonPromptDecorator


class Pair(NamedTuple):
    stock: Stock
    task: Awaitable


class StocksSpliterByAvailability:

    async def init_stocks(self):
        if config.DEBUG_MODE:
            res = (await TinkoffClient.get_stocks())[:10]
        else:
            res = await TinkoffClient.get_stocks()
        return res

    async def split_by_availability(self, stocks: None) -> dict[str, [Stock]]:
        if not stocks:
            stocks = await self.init_stocks()
        logger.info(len(stocks))
        self.count_err = 0
        self.count_succ = 0
        req_partial = partial(LimitOrderReq, lots=0, operation=OperationEnum.BUY, price=Decimal('0'))
        pairs: [Pair] = [Pair(stock, TinkoffClient.create_limit_order(req_partial(figi=stock.figi)))
                         for stock in stocks]
        self.available_stocks: [Stock] = []
        self.unavailable_stocks: [Stock] = []
        while True:
            stocks: [Stock]
            tasks: [Awaitable]
            stocks, tasks = zip(*pairs)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.on_repeat = []
            for stock, result in zip(stocks, results):
                self._put_to_res_list_in_accordance_with_availability(stock, result)
            pairs = [Pair(stock, TinkoffClient.create_limit_order(req_partial(figi=stock.figi)))
                     for stock in self.on_repeat]
            if not pairs:
                logger.info(f'count of 429 code equals {self.count_err}')
                logger.info(f'count of success equals {self.count_succ}')
                return {'available': self.available_stocks, 'unavailable': self.unavailable_stocks}

    def _put_to_res_list_in_accordance_with_availability(self, stock, result):
        if isinstance(result, ExternalServiceError):
            if result.code == 429:
                self._put_on_repeat(stock)
            else:
                self._put_to_res_list(stock, result)
        elif isinstance(result, Exception):
            raise result

    def _put_on_repeat(self, stock):
        self.count_err += 1
        self.on_repeat.append(stock)

    def _put_to_res_list(self, stock, result):
        self.count_succ += 1
        key = result.detail
        if key == 'Instrument is disabled for trading':
            self.unavailable_stocks.append(stock)
        else:
            self.available_stocks.append(stock)


class StocksSpliterByAvailabilityWithPrompt(StocksSpliterByAvailability):
    @JsonPromptDecorator('stocks_split_by_availability', dict[str, list[Stock]])
    @timeit
    async def split_by_availability(self) -> dict[str, [Stock]]:
        return await super().split_by_availability()


if __name__ == '__main__':
    async def main():
        try:
            with print_timing():
                res = await StocksSpliterByAvailabilityWithPrompt().split_by_availability()
                pprint(res)
            await client.aclose()
        finally:
            sound_notifier()

    asyncio.set_event_loop_policy(TimedEventLoopPolicy())
    asyncio.run(main())
