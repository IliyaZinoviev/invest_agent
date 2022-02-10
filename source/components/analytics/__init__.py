import asyncio
import json
from datetime import datetime
from itertools import product
from time import sleep

from aiohttp import ClientSession

from source.components.analytics.request_handlers import get_stock_candles
from source.components.analytics.stock_analyzer import StockAnalyzer
from source.components.common import intervals
from source.components.common.request_handlers import get_figies_and_min_price_incs
from source.components.models import Stock, StockAnalytics
from source.app.config import config
from source.app.extentions import create_db_engine, db_engine_provider, session_provider
from source.utils.utils import atimeit


def limit_iter(struct, delay, parts_count):
    struct_length = len(struct)
    curr_parts_count = struct_length // parts_count + struct_length % parts_count
    for ind in range(curr_parts_count):
        start = datetime.now()
        yield ind
        end = datetime.now() - start
        curr_delay = delay - end.total_seconds()
        if curr_delay > 0 and ind + 1 != curr_parts_count:
            sleep(curr_delay)


async def analyze(figies, min_price_incs):
    requests_count_constraint = 120
    delay = 60
    requests_count_per_task = 30
    offset = parts_count = requests_count_constraint // requests_count_per_task

    stocks_data = {}
    max_possible_profits = {}
    analytics = {ticker: {} for ticker in config.TICKERS}
    ticker_interval_tuples = list(product(config.TICKERS, intervals))

    for ind in limit_iter(ticker_interval_tuples, delay, parts_count):
        tasks = [get_stock_candles(ticker, figies[ticker], interval)
                 for ticker, interval, in ticker_interval_tuples[ind*offset:ind*offset+offset]]
        results = await asyncio.gather(*tasks)
        for ticker, interval, candles in results:
            # logger.info(f'{ticker}, {interval}: \n{pformat(analytics)}')
            stock_analyzer = StockAnalyzer(candles, min_price_incs[ticker])
            analytics[ticker][interval] = stock_analyzer.stock_analytics
            update_stocks_data(stock_analyzer.stock_data, stocks_data, max_possible_profits, ticker,
                               figies, min_price_incs, interval)
    return analytics, stocks_data


async def save_analytics(analytics_dict):
    json_data = json.dumps(analytics_dict)
    engine = db_engine_provider[0]
    async with engine.acquire() as conn:
        await conn.execute(StockAnalytics.update().values(data=json_data).where(StockAnalytics.c.id == 1))


async def save_stocks(stocks_data):
    json_data = json.dumps(stocks_data)
    engine = db_engine_provider[0]
    async with engine.acquire() as conn:
        await conn.execute(Stock.update().values(data=json_data).where(Stock.c.id == 1))


def update_stocks_data(stock_data, stocks_data, max_possible_profits, ticker, figies, min_price_incs, interval):
    curr_max_possible_profit = stock_data['possible_profit']
    if ticker not in max_possible_profits or max_possible_profits[ticker] < curr_max_possible_profit:
        max_possible_profits[ticker] = curr_max_possible_profit
        stock_data = {**{'interval': interval, 'figi': figies[ticker], 'min_price_inc': min_price_incs[ticker]},
                      **stock_data}
        stocks_data[ticker] = stock_data


@atimeit
async def start_analyze():
    async with ClientSession() as session:
        session_provider.append(session)
        figies, min_price_incs = await get_figies_and_min_price_incs()
        analytics, stocks_data = await analyze(figies, min_price_incs)
        session_provider.pop()
    async with await create_db_engine() as engine:
        db_engine_provider.append(engine)
        await save_analytics(analytics)
        await save_stocks(stocks_data)
        db_engine_provider.pop()
