import asyncio
import json
from datetime import datetime
from pprint import pformat
from time import sleep

from source.common import request, intervals_vals_dict, get_fee
from source.config import URL
from source.extentions import logger
from source.requests_input_data_makers import (make_limit_order_params, make_limit_order_body, make_candles_params,
                                               params, headers)


async def have_limit_order(figi: str, ticker: str) -> bool:
    url = URL + 'orders'
    response_data = await request(url, headers, have_limit_order.__name__, params=params, ticker=ticker)
    for limit_order in response_data['payload']:
        if figi == limit_order['figi']:
            return True
    return False


async def is_stock_in_portfolio(figi: str, ticker: str) -> bool:
    url = URL + 'portfolio'
    response_data = await request(url, headers, is_stock_in_portfolio.__name__, params=params, ticker=ticker)
    for position in response_data['payload']['positions']:
        if figi == position['figi']:
            return True
    return False


async def get_buying_price(ticker: str) -> float:
    url = URL + 'portfolio'
    response_data = await request(url, headers, is_stock_in_portfolio.__name__, params=params, ticker=ticker)
    for position in response_data['payload']['positions']:
        if ticker == position['ticker']:
            return position['averagePositionPrice']['value']
    return False


async def get_current_cost(figi: str, ticker: str, interval: str) -> float or None:
    url = URL + 'market/candles'
    params = make_candles_params(interval, 'minutes', intervals_vals_dict[interval], figi)
    response_data = await request(url, headers, get_current_cost.__name__, params=params, ticker=ticker)
    candles = response_data['payload']['candles']
    if len(candles) != 0:
        return candles[-1]['l']
    else:
        return None


async def make_limit_order_on_purchase(figi: str = None, ticker: str = None, price: float = None):
    url = URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Buy', price)
    response_data = await request(url, headers, make_limit_order_on_purchase.__name__,
                                  params=params, body=body, ticker=ticker)
    logger.info(response_data['payload'])


async def make_limit_order_on_sell(figi: str = None, ticker: str = None, price: float = None):
    url = URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Sell', price)
    response_data = await request(url, headers, make_limit_order_on_sell.__name__, params=params, body=body,
                                  ticker=ticker)
    logger.info(response_data['payload'])


async def manage_stock(figi, ticker, interval, buying_ratio, selling_ratio, possible_profit, current_profit):
    try:
        if not await have_limit_order(figi, ticker):
            if not await is_stock_in_portfolio(figi, ticker):
                if current_price := await get_current_cost(figi, ticker, interval):
                    logger.info(f'price: {current_price}')
                    buying_price = current_price * (100 - buying_ratio) / 100
                    await make_limit_order_on_purchase(figi, buying_price)
                else:
                    logger.info(f'manage_stock({ticker}): candles is not available.')
            elif buying_price := await get_buying_price(ticker):
                celling_price = buying_price * (100 - selling_ratio) / 100
                await make_limit_order_on_sell(figi, celling_price)
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


async def start_monitoring_agent(sorted_stocks):
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
        tasks = [manage_stock(figi, ticker, interval, buying_ratio, selling_ration, possible_profit, current_profit)
                 for figi, ticker, interval, possible_profit, buying_ratio, selling_ration, current_profit
                 in map(lambda stock, curr_profit: stock + (curr_profit,), sorted_stocks, current_profits)]
        current_profits = await asyncio.gather(*tasks)
    return [(stock[1], stock[3], curr_profit) for stock, curr_profit in zip(sorted_stocks, current_profits)]


def get_daily_result(daily_result_data):
    return {ticker: [possible_profit, curr_profit]
            for ticker, possible_profit, curr_profit in daily_result_data}


def save_daily_result(daily_result):
    logger.info(pformat(daily_result))
    with open('daily_result.json', 'w') as file:
        json.dump(daily_result, file)
