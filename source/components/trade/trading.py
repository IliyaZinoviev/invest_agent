import asyncio
import json
from datetime import datetime
from pprint import pformat
from time import sleep
from round_utils import ceil, floor

from components.common import get_fee
from components.trade.request_handlers import have_limit_order, is_stock_in_portfolio, get_current_cost, \
    make_limit_order_on_purchase, get_buying_price, make_limit_order_on_sell
from components.trade.sandbox import clear_sandbox_portfolio, set_currencies_balance
from components.trade.stocks_data import get_sorted_stocks
from core.extentions import logger, session


async def manage_stock(*args):
    figi, ticker, min_price_inc, interval, buying_ratio, selling_ratio, possible_profit, current_profit = args
    try:
        if not await have_limit_order(figi, ticker):
            if not await is_stock_in_portfolio(figi, ticker):
                if current_price := await get_current_cost(figi, ticker, interval):
                    logger.info(f'price: {current_price}')
                    buying_price = floor(current_price * (100 - buying_ratio) / 100, min_price_inc)
                    await make_limit_order_on_purchase(figi, ticker, buying_price)
                else:
                    logger.info(f'manage_stock({ticker}): candles is not available.')
            elif buying_price := await get_buying_price(ticker):
                celling_price = ceil(buying_price * (100 - selling_ratio) / 100, min_price_inc)
                await make_limit_order_on_sell(figi, ticker, celling_price)
                current_profit += celling_price - buying_price - get_fee(buying_price, celling_price)
            else:
                logger.info(f'manage_stock({ticker}): portfolio is not available.')
        else:
            logger.info(f'manage_stock({ticker}): ticker has limit order.')
    except Exception as e:
        logger.info(e)
    finally:
        logger.info(f'manage_stock({ticker}): goal: {possible_profit / 30}; current: {current_profit} '
                    f'( {current_profit / possible_profit * 100}% )')
        return current_profit


async def trade(sorted_stocks):
    sorted_stocks_length = len(sorted_stocks)
    limit_count = 50 // sorted_stocks_length
    curr_count = 0
    current_profits = [0 for _ in range(sorted_stocks_length)]
    while datetime.now().hour != 3:
        if curr_count == limit_count:
            end = datetime.now() - start  # noqa F821
            delay = 60 - end.total_seconds()
            logger.info(f'delay: {delay}s')
            if delay > 0:
                sleep(delay)
            curr_count = 0
        curr_count += 1
        if curr_count == 1:
            start = datetime.now() # noqa F841
        tasks = [manage_stock(figi, ticker, min_price_inc, interval, buying_ratio, selling_ration, possible_profit,
                              current_profit)
                 for figi, ticker, min_price_inc, interval, possible_profit, buying_ratio, selling_ration,
                 current_profit
                 in map(lambda stock, curr_profit: stock + (curr_profit,), sorted_stocks, current_profits)]
        current_profits = await asyncio.gather(*tasks)
    return current_profits


def get_daily_result(daily_result_data: list) -> dict:
    return {ticker: [possible_profit, curr_profit]
            for ticker, possible_profit, curr_profit in daily_result_data}


def save_daily_result(daily_result: dict):
    logger.info(pformat(daily_result))
    with open('daily_result.json', 'w') as file:
        json.dump(daily_result, file)


async def start_trade():
    sorted_stocks = get_sorted_stocks()
    async with session:
        await clear_sandbox_portfolio()
        await set_currencies_balance()
        current_profits = await trade(sorted_stocks)
    daily_result_data = [(stock[1], stock[3], curr_profit)
                         for stock, curr_profit in zip(sorted_stocks, current_profits)]
    daily_result = get_daily_result(daily_result_data)
    save_daily_result(daily_result)
