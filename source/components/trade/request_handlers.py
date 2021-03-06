from components.common import intervals_vals_dict
from components.common.request_handlers import request
from core.config import config
from core.extentions import logger
from components.common.request_input_data_makers import (make_limit_order_params, make_limit_order_body,
                                                         make_candles_params, params, headers)


async def have_limit_order(figi: str, ticker: str) -> bool:
    url = config.URL + 'orders'
    response_data = await request(url, headers, have_limit_order.__name__, params=params, ticker=ticker)
    for limit_order in response_data['payload']:
        if figi == limit_order['figi']:
            return True
    return False


async def is_stock_in_portfolio(figi: str, ticker: str) -> bool:
    url = config.URL + 'portfolio'
    response_data = await request(url, headers, is_stock_in_portfolio.__name__, params=params, ticker=ticker)
    for position in response_data['payload']['positions']:
        if figi == position['figi']:
            return True
    return False


async def get_buying_price(ticker: str) -> float:
    url = config.URL + 'portfolio'
    response_data = await request(url, headers, is_stock_in_portfolio.__name__, params=params, ticker=ticker)
    for position in response_data['payload']['positions']:
        if ticker == position['ticker']:
            return position['averagePositionPrice']['value']
    return False


async def get_current_cost(figi: str, ticker: str, interval: str) -> float or None:
    url = config.URL + 'market/candles'
    params = make_candles_params(interval, 'minutes', intervals_vals_dict[interval], figi)
    response_data = await request(url, headers, get_current_cost.__name__, params=params, ticker=ticker)
    candles = response_data['payload']['candles']
    if len(candles) != 0:
        return candles[-1]['l']
    else:
        return None


async def make_limit_order_on_purchase(figi: str, ticker: str, price: float):
    url = config.URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Buy', price)
    response_data = await request(url, headers, make_limit_order_on_purchase.__name__,
                                  method='post', params=params, body=body, ticker=ticker)
    logger.info(response_data['payload'])


async def make_limit_order_on_sell(figi: str, ticker: str, price: float):
    url = config.URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Sell', price)
    response_data = await request(url, headers, make_limit_order_on_sell.__name__,
                                  method='post', params=params, body=body, ticker=ticker)
    logger.info(response_data['payload'])
