import asyncio
import json
from datetime import datetime
from pprint import pformat
from time import sleep

from aiohttp import ClientSession
from components.common import get_fee
from components.models import DailyResult
from components.trade.request_handlers import (
    get_buying_price, get_current_cost, have_limit_order, is_stock_in_portfolio, make_limit_order_on_purchase,
    make_limit_order_on_sell)
from components.trade.sandbox import clear_sandbox_portfolio, set_currencies_balance
from components.trade.stocks_data import get_sorted_stocks
from app.config import config
from app.extentions import create_db_engine, db_engine_provider, logger, session_provider
from pytz import timezone
from round_utils import ceil, floor


async def manage_stock(
        current_profit,
        buying_prices,
        figi=None,
        ticker=None,
        min_price_inc=None,
        interval=None,
        buying_ratio=None,
        selling_ratio=None,
        possible_profit=None
):
    try:
        if not await have_limit_order(figi, ticker):
            if not await is_stock_in_portfolio(figi, ticker):
                if current_price := await get_current_cost(figi, ticker, interval):
                    logger.info(f'price: {current_price}')
                    buying_price = floor((current_price - min_price_inc) * (100 - buying_ratio) / 100, min_price_inc)
                    buying_prices[ticker] = buying_price
                    await make_limit_order_on_purchase(figi, ticker, buying_price)
                else:
                    logger.info(f'manage_stock({ticker}): candles is not available.')
            elif (buying_price := buying_prices[ticker]) or (buying_price := await get_buying_price(ticker)):
                selling_price = (buying_price + min_price_inc) * (100 + selling_ratio) / 100
                selling_price = ceil(selling_price + get_fee(buying_price, selling_price),
                                     min_price_inc)
                await make_limit_order_on_sell(figi, ticker, selling_price)
                current_profit += selling_price - buying_price - get_fee(buying_price, selling_price)
            else:
                logger.info(f'manage_stock({ticker}): portfolio is not available.')
        else:
            logger.info(f'manage_stock({ticker}): ticker has limit order.')
    except Exception as e:
        logger.info(e)
    finally:
        daily_possible_profit = possible_profit / 30
        logger.info(f'manage_stock({ticker}): goal: {daily_possible_profit}; current: {current_profit} '
                    f'( {current_profit / daily_possible_profit * 100}% )')
        return ticker, current_profit


async def trade(stocks):
    sorted_stocks_length = len(stocks)
    buying_prices = {stock['ticker']: None for stock in stocks}
    limit_count = 50 // sorted_stocks_length
    curr_count = 0
    current_profits = {stock['ticker']: 0 for stock in stocks}
    while (lambda now: now.hour != 1 and now.minute != 45)(datetime.now(tz=timezone('Europe/Moscow'))):
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
        tasks = [manage_stock(current_profits[stock['ticker']], buying_prices, **stock) for stock in stocks]
        current_profits = dict(await asyncio.gather(*tasks))
    return current_profits


def get_daily_result(daily_result_data: list) -> dict:
    return {ticker: [possible_profit, curr_profit]
            for ticker, possible_profit, curr_profit in daily_result_data}


async def save_daily_result(daily_result: dict):
    logger.info(pformat(daily_result))

    json_data = json.dumps(daily_result)
    engine = db_engine_provider[0]
    async with engine.acquire() as conn:
        await conn.execute(DailyResult.update().values(data=json_data).where(DailyResult.c.id == 1))


async def start_trade():
    async with await create_db_engine() as engine,\
            ClientSession() as session:
        db_engine_provider.append(engine)
        sorted_stocks = await get_sorted_stocks()

        session_provider.append(session)
        if config.IS_SANDBOX_MODE:
            await clear_sandbox_portfolio()
            await set_currencies_balance('USD', 100000)
            await set_currencies_balance('RUB', 100000)
        current_profits = await trade(sorted_stocks)
        session_provider.pop()

        daily_result_data = [(stock[1], stock[3], curr_profit)
                             for stock, curr_profit in zip(sorted_stocks, current_profits)]
        daily_result = get_daily_result(daily_result_data)
        await save_daily_result(daily_result)

        db_engine_provider.pop()
