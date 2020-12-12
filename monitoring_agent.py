import asyncio
import logging
from datetime import datetime, timedelta, timezone
from aiohttp import ClientSession

from common import headers, market_url, broker_acc_id_param, get_figi, price_percentage_ratio_for_sell, \
    price_percentage_ratio_for_purchase
from config import TICKERS


async def have_limit_order(session: ClientSession, figi: str, ticker: str) -> bool:
    params = [broker_acc_id_param]
    async with session.get(market_url + 'orders',
                           params=params,
                           headers=headers) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'have_limit_order({ticker}): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            for limit_order in response_data['payload']:
                if figi == limit_order['figi']:
                    return True
            return False
        else:
            raise Exception(f'have_limit_order({ticker}): {resp_code}, {response_data}')


async def is_stock_in_portfolio(session: ClientSession, figi: str, ticker: str) -> bool:
    params = [broker_acc_id_param]
    async with session.get(market_url + 'portfolio',
                           params=params,
                           headers=headers) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'is_stock_in_portfolio({ticker}): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            for position in response_data['payload']['positions']:
                if figi == position['figi']:
                    return True
            return False
        else:
            raise Exception(f'is_stock_in_portfolio({ticker}): {resp_code}, {response_data}')


async def get_average_price(session: ClientSession, figi: str, ticker: str) -> (str, float):
    now = datetime.now(tz=timezone(timedelta(0)))
    then = now - timedelta(weeks=4)
    params = [('figi', figi),
              ('from', then.isoformat()),
              ('to', now.isoformat()),
              ('interval', 'month')]
    async with session.get(market_url + 'market/candles',
                           params=params,
                           headers=headers) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'get_average_price({ticker}): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            candles = response_data['payload']['candles']
            average_price = (candles[-1]['h'] + candles[-1]['l']) / 2
            logging.info(f'{ticker}: {average_price}')
            return figi, average_price
        else:
            raise Exception(f'get_average_price({ticker}): {resp_code}, {response_data}')


async def get_current_cost(session: ClientSession, figi: str, ticker: str) -> float or None:
    now = datetime.now(tz=timezone(timedelta(0)))
    then = now - timedelta(minutes=6)
    params = [('figi', figi),
              ('from', then.isoformat()),
              ('to', now.isoformat()),
              ('interval', '5min')]
    async with session.get(market_url + 'market/candles',
                           params=params,
                           headers=headers) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'get_current_cost({ticker}): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            candles = response_data['payload']['candles']
            if len(candles) != 0:
                return (candles[-1]['h'] + candles[-1]['l']) / 2
            else:
                return None
        else:
            raise Exception(f'get_current_cost({ticker}): {resp_code}, {response_data}')


async def make_limit_order_on_purchase(session: ClientSession, figi: str, ticker: str, price: float):
    params = [('figi', figi), broker_acc_id_param]
    body = {'lots': 1,
            'operation': 'Buy',
            'price': price}
    async with session.post(market_url + 'orders/limit-order',
                            params=params,
                            headers=headers,
                            json=body) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'make_limit_order_on_purchase({ticker}): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            logging.info(response_data['payload'])
        else:
            raise Exception(f'make_limit_order_on_purchase({ticker}): {resp_code}, {response_data}')


async def make_limit_order_on_sell(session: ClientSession, figi: str, ticker: str, price: float):
    params = [('figi', figi), broker_acc_id_param]
    body = {'lots': 1,
            'operation': 'Sell',
            'price': price}
    response = await session.post(market_url + 'orders/limit-order',
                                  params=params,
                                  headers=headers,
                                  json=body)
    resp_code = response.status
    if resp_code in [429, 401]:
        raise Exception(f'make_limit_order_on_sell({ticker}): {resp_code}, {response.reason}')
    response_data = await response.json()
    if resp_code == 200:
        logging.info(response_data['payload'])
    else:
        raise Exception(f'make_limit_order_on_sell({ticker}): {resp_code}, {response_data}')


def is_profitably_purchase(price: float, average_price: float, ticker: str) -> bool:
    ratio = 100 - price / average_price * 100
    decision = price < average_price and ratio > price_percentage_ratio_for_purchase
    logging.info(f'is_profitably_purchase({ticker}): {price}, {average_price}, {decision}, {ratio}')
    return decision


def is_profitably_sell(price: float, average_price: float, ticker: str) -> bool:
    ratio = 100 - average_price / price * 100
    decision = price > average_price and ratio > price_percentage_ratio_for_sell
    logging.info(f'is_profitably_sell({ticker}): {price}, {average_price}, {decision}, {ratio}')
    return decision


async def manage_stock(session, figi, ticker, average_price):
    try:
        if not await have_limit_order(session, figi, ticker):
            if price := await get_current_cost(session, figi, ticker):
                logging.info(f'price: {price}')
                if not await is_stock_in_portfolio(session, figi, ticker):
                    if is_profitably_purchase(price, average_price, ticker):
                        await make_limit_order_on_purchase(session, figi, ticker, price)
                elif is_profitably_sell(price, average_price, ticker):
                    await make_limit_order_on_sell(session, figi, ticker, price)
            else:
                logging.info(f'manage_stock({ticker}): candles is not available.')
        else:
            logging.info(f'manage_stock({ticker}): ticker has limit order.')
    except Exception as e:
        logging.info(e)


async def start_monitoring_agent():
    async with ClientSession() as session:
        tasks = [get_figi(session, ticker)
                 for ticker in TICKERS]
        ticker_figi_tuples = await asyncio.gather(*tasks)
        tasks = [get_average_price(session, figi, ticker)
                 for ticker, figi in ticker_figi_tuples]
        average_prices = {figi: average_price for figi, average_price in await asyncio.gather(*tasks)}
        while True:
            tasks = [manage_stock(session, figi, ticker, average_prices[figi])
                     for ticker, figi in ticker_figi_tuples]
            await asyncio.gather(*tasks)
            await asyncio.sleep(5)
