import asyncio
import json
from datetime import datetime
from itertools import product
from time import sleep

from components.analytics.request_handlers import get_stock_candles
from components.common import intervals
from components.common.request_handlers import get_figies_and_min_price_incs
from core.extentions import logger, session  # noqa F401
from core.config import TICKERS
from components.analytics.stock_analyzer import StockAnalyzer
from utils.utils import atimeit


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
    analytics = {ticker: {} for ticker in TICKERS}
    ticker_interval_tuples = list(product(TICKERS, intervals))

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


def save_analytics(analytics_dict):
    with open('../analytics.json', 'w') as file:
        json.dump(analytics_dict, file)


def save_stocks(stocks_data):
    with open('../stocks.json', 'w') as file:
        json.dump(stocks_data, file)


def update_stocks_data(stock_data, stocks_data, max_possible_profits, ticker, figies, min_price_incs, interval):
    curr_max_possible_profit = stock_data['possible_profit']
    if ticker not in max_possible_profits or max_possible_profits[ticker] < curr_max_possible_profit:
        max_possible_profits[ticker] = curr_max_possible_profit
        stock_data = {**{'interval': interval, 'figi': figies[ticker], 'min_price_inc': min_price_incs[ticker]},
                      **stock_data}
        stocks_data[ticker] = stock_data


@atimeit
async def start_analyze():
    async with session:
        figies, min_price_incs = await get_figies_and_min_price_incs()
        analytics, stocks_data = await analyze(figies, min_price_incs)
    save_analytics(analytics)
    save_stocks(stocks_data)
