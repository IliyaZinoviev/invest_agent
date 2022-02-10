from components.common.request_handlers import request
from components.common.request_input_data_makers import (
    headers, make_limit_order_body, make_limit_order_params, params)
from app.config import config
from app.extentions import logger

from source.components.common.request_handlers import get_candles


async def have_limit_order(figi: str, ticker: str) -> bool:
    url = config.BASE_URL + 'orders'
    response_data = await request(url, headers, have_limit_order.__name__, params=params, ticker=ticker)
    for limit_order in response_data['payload']:
        if figi == limit_order['figi']:
            return True
    return False


async def is_stock_in_portfolio(figi: str, ticker: str) -> bool:
    url = config.BASE_URL + 'portfolio'
    response_data = await request(url, headers, is_stock_in_portfolio.__name__, params=params, ticker=ticker)
    for position in response_data['payload']['positions']:
        if figi == position['figi']:
            return True
    return False


async def get_buying_price(ticker: str) -> float:
    url = config.BASE_URL + 'portfolio'
    response_data = await request(url, headers, is_stock_in_portfolio.__name__, params=params, ticker=ticker)
    for position in response_data['payload']['positions']:
        if ticker == position['ticker']:
            return position['averagePositionPrice']['value']
    return False


async def get_current_cost(figi: str, ticker: str, interval: str) -> float or None:
    candles = await get_candles(figi, ticker, interval)
    if len(candles) != 0:
        return candles[-1]['l']
    else:
        return None


async def make_limit_order_on_purchase(figi: str, ticker: str, price: float):
    url = config.BASE_URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Buy', price)
    response_data = await request(url, headers, make_limit_order_on_purchase.__name__,
                                  method='post', params=params, body=body, ticker=ticker)
    logger.info(response_data['payload'])


async def make_limit_order_on_sell(figi: str, ticker: str, price: float):
    url = config.BASE_URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Sell', price)
    response_data = await request(url, headers, make_limit_order_on_sell.__name__,
                                  method='post', params=params, body=body, ticker=ticker)
    logger.info(response_data['payload'])
