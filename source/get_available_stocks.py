import asyncio
from decimal import Decimal
from functools import partial
from typing import NamedTuple, Awaitable

from app.extentions import logger
from clients.tinkoff_invest.api import client, ExternalServiceError
from clients.tinkoff_invest.client import TinkoffClient
from components.common.enums import OperationEnum
from helpers.policies import TimedEventLoopPolicy, print_timing
from serializers.tinkoff_invest.request import LimitOrderReq
from serializers.tinkoff_invest.common import Stock
from utils.utils import atimeit, timeit
from utils.json.prompt import JsonFileMetaData, JsonPromptDecorator


class Pair(NamedTuple):
    stock: Stock
    task: Awaitable


class InvestAgent:
    #
    # @staticmethod
    # async def filter_only_active_old(stocks: [Stock]) -> [Stock]:
    #     try:
    #         count = 0
    #         # limit = 610
    #         # delay = 5
    #         limit = 100
    #         delay = 60
    #         req_partial = partial(LimitOrderReq, lots=0, operation=OperationEnum.BUY, price=Decimal('0'))
    #         pairs: [Pair] = [Pair(stock, TinkoffClient.create_limit_order(req_partial(figi=stock.figi)))
    #                          for stock in stocks]
    #         #
    #         # now_dt = datetime.now(tz=timezone(timedelta(hours=3)))
    #         # pairs += [Pair(stocks[0], TinkoffClient.get_orderbook(stocks[0], 1)) for i in range(239)]
    #         # pairs += [Pair(stocks[0], TinkoffClient.get_active_orders()) for i in range(100)]
    #         # pairs += [Pair(stocks[0], TinkoffClient.get_portfolio()) for i in range(120)]
    #         # pairs += [Pair(stocks[0], TinkoffClient.cancel_order(CancelOrderReq(id_=100000))) for i in range(50)]
    #         # pairs += [Pair(stocks[0], TinkoffClient.get_operations(OperationsReq(
    #         #     to=now_dt.isoformat(),
    #         #     from_=(now_dt - timedelta(days=14)).isoformat(),
    #         # ))) for i in range(120)]
    #         accessible_stocks: [Stock] = []
    #         async for ind in limit_iter(pairs, delay, limit):
    #             stocks: [Stock]
    #             tasks: [Awaitable]
    #             end: int = (ind + 1) * limit
    #             stocks, tasks = zip(*pairs[ind * limit:end])
    #             results = await asyncio.gather(*tasks, return_exceptions=True)
    #             on_repeat = []
    #             for stock, result in zip(stocks, results):
    #                 if isinstance(result, ExternalServiceError):
    #                     key = result.detail
    #                     if result.code == 429:
    #                         count += 1
    #                         on_repeat.append(stock)
    #                     else:
    #                         if key != 'Instrument is disabled for trading':
    #                             accessible_stocks.append(stock)
    #                 else:
    #                     raise result
    #             pairs[end:end] = [Pair(stock, TinkoffClient.create_limit_order(req_partial(figi=stock.figi)))
    #                               for stock in on_repeat]
    #         logger.info(f'count of 429 code equals {count}')
    #         return accessible_stocks
    #     except Exception:
    #         raise
    available_stocks_metadata = JsonFileMetaData('available_stocks')

    @staticmethod
    @JsonPromptDecorator(available_stocks_metadata.path, f'read {available_stocks_metadata.name} or rewrite? [rwi]')
    @timeit
    async def split_by_availability() -> dict[str, [Stock]]:
        try:
            stocks = await TinkoffClient.get_stocks()
            logger.info(len(stocks))
            count_err = 0
            count_succ = 0
            req_partial = partial(LimitOrderReq, lots=0, operation=OperationEnum.BUY, price=Decimal('0'))
            pairs: [Pair] = [Pair(stock, TinkoffClient.create_limit_order(req_partial(figi=stock.figi)))
                             for stock in stocks]
            # now_dt = datetime.now(tz=timezone(timedelta(hours=3)))
            # pairs += [Pair(stocks[0], TinkoffClient.get_orderbook(stocks[0], 1)) for i in range(460)]
            # pairs += [Pair(stocks[0], TinkoffClient.get_active_orders()) for i in range(200)]
            # pairs += [Pair(stocks[0], TinkoffClient.get_portfolio()) for i in range(240)]
            # pairs += [Pair(stocks[0], TinkoffClient.cancel_order(CancelOrderReq(id_=100000))) for i in range(100)]
            # pairs += [Pair(stocks[0], TinkoffClient.get_operations(OperationsReq(
            #     to=now_dt.isoformat(),
            #     from_=(now_dt - timedelta(days=14)).isoformat(),
            # ))) for i in range(240)]
            available_stocks: [Stock] = []
            unavailable_stocks: [Stock] = []
            while True:
                stocks: [Stock]
                tasks: [Awaitable]
                stocks, tasks = zip(*pairs)
                results = await asyncio.gather(*tasks, return_exceptions=True)
                on_repeat = []
                for stock, result in zip(stocks, results):
                    if isinstance(result, Exception):
                        if isinstance(result, ExternalServiceError):
                            key = result.detail
                            if result.code == 429:
                                count_err += 1
                                on_repeat.append(stock)
                            else:
                                count_succ += 1
                                if key == 'Instrument is disabled for trading':
                                    unavailable_stocks.append(stock)
                                else:
                                    available_stocks.append(stock)

                        else:
                            raise result
                pairs = [Pair(stock, TinkoffClient.create_limit_order(req_partial(figi=stock.figi)))
                         for stock in on_repeat]
                if not pairs:
                    logger.info(f'count of 429 code equals {count_err}')
                    logger.info(f'count of success equals {count_succ}')
                    return {'available': available_stocks, 'unavailable': unavailable_stocks}
        except Exception:
            raise

    # @staticmethod
    # async def filter_only_active_sync(stocks: [Stock]) -> [Stock]:
    #     print(len(stocks))
    #     try:
    #         count = 0
    #         req_partial = partial(LimitOrderReq, lots=0, operation=OperationEnum.BUY, price=Decimal('0'))
    #         accessible_stocks: [Stock] = []
    #         while True:
    #             on_repeat = []
    #             for stock in stocks:
    #                 try:
    #                     res = await TinkoffClient.create_limit_order(req_partial(figi=stock.figi))
    #                 except Exception as result:
    #                     if isinstance(result, ExternalServiceError):
    #                         key = result.detail
    #                         if result.code == 429:
    #                             count += 1
    #                             on_repeat.append(stock)
    #                         else:
    #                             if key != 'Instrument is disabled for trading':
    #                                 accessible_stocks.append(stock)
    #                     else:
    #                         raise result
    #             if not on_repeat:
    #                 break
    #             else:
    #                 stocks = on_repeat
    #         logger.info(f'count of 429 code equals {count}')
    #         return accessible_stocks
    #     except Exception:
    #         raise


async def main():
    with print_timing():
        available_stocks = await InvestAgent.split_by_availability()
    await client.aclose()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(TimedEventLoopPolicy())
    asyncio.run(main())