import asyncio
import logging

from source.analytics import percentage_ratio
from source.common import MARKET_URL, request
from source.requests_makers import make_limit_order_params, make_limit_order_body, make_candles_params, params, headers

price_percentage_ratio_for_purchase = 3  # TODO add formula for it
price_percentage_ratio_for_sell = 0  # TODO add formula for it


async def have_limit_order(figi: str, ticker: str) -> bool:
    url = MARKET_URL + 'orders'
    response_data = await request(url, headers, params, have_limit_order.__name__, ticker=ticker)
    for limit_order in response_data['payload']:
        if figi == limit_order['figi']:
            return True
    return False


async def is_stock_in_portfolio(figi: str, ticker: str) -> bool:
    url = MARKET_URL + 'portfolio'
    response_data = await request(url, headers, params, is_stock_in_portfolio.__name__, ticker=ticker)
    for position in response_data['payload']['positions']:
        if figi == position['figi']:
            return True
    return False


async def get_average_price(figi: str = None, ticker: str = None) -> (str, float):
    url = MARKET_URL + 'market/candles'
    params = make_candles_params('month', 'weeks', 4, figi)
    response_data = await request(url, headers, params, get_average_price.__name__, ticker=ticker)
    candles = response_data['payload']['candles']
    average_price = (candles[-1]['h'] + candles[-1]['l']) / 2
    logging.info(f'{ticker}: {average_price}')
    return figi, average_price


async def get_current_cost(figi: str = None, ticker: str = None) -> float or None:
    url = MARKET_URL + 'market/candles'
    params = make_candles_params('5min', 'minutes', 6, figi)
    response_data = await request(url, headers, params, get_current_cost.__name__, ticker=ticker)
    candles = response_data['payload']['candles']
    if len(candles) != 0:
        return (candles[-1]['h'] + candles[-1]['l']) / 2
    else:
        return None


async def make_limit_order_on_purchase(figi: str = None, ticker: str = None, price: float = None):
    url = MARKET_URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Buy', price)
    response_data = await request(url, headers, params, make_limit_order_on_purchase.__name__, body=body, ticker=ticker)
    logging.info(response_data['payload'])


async def make_limit_order_on_sell(figi: str = None, ticker: str = None, price: float = None):
    url = MARKET_URL + 'orders/limit-order'
    params = make_limit_order_params(figi)
    body = make_limit_order_body('Sell', price)
    response_data = await request(url, headers, params, make_limit_order_on_sell.__name__, body=body, ticker=ticker)
    logging.info(response_data['payload'])


def is_profitably_purchase(price: float, average_price: float, ticker: str) -> bool:
    ratio = percentage_ratio(price, average_price)
    decision = price < average_price and ratio > price_percentage_ratio_for_purchase
    logging.info(f'is_profitably_purchase({ticker}): {price}, {average_price}, {decision}, {ratio}')
    return decision


def is_profitably_sell(price: float, average_price: float, ticker: str) -> bool:
    ratio = percentage_ratio(price, average_price)
    decision = price > average_price and ratio > price_percentage_ratio_for_sell
    logging.info(f'is_profitably_sell({ticker}): {price}, {average_price}, {decision}, {ratio}')
    return decision


async def manage_stock(figi, ticker, average_price):
    try:
        if not await have_limit_order(figi, ticker):
            if price := await get_current_cost(figi, ticker):
                logging.info(f'price: {price}')
                if not await is_stock_in_portfolio(figi, ticker):
                    if is_profitably_purchase(price, average_price, ticker):
                        await make_limit_order_on_purchase(figi, price)
                elif is_profitably_sell(price, average_price, ticker):
                    await make_limit_order_on_sell(figi, price)
            else:
                logging.info(f'manage_stock({ticker}): candles is not available.')
        else:
            logging.info(f'manage_stock({ticker}): ticker has limit order.')
    except Exception as e:
        logging.info(e)


async def start_monitoring_agent(figies):
    tasks = [get_average_price(figi, ticker)
             for ticker, figi in figies.items()]
    average_prices = {figi: average_price for figi, average_price in await asyncio.gather(*tasks)}
    while True:
        tasks = [manage_stock(figi, ticker, average_prices[figi])
                 for ticker, figi in figies.items()]
        await asyncio.gather(*tasks)
