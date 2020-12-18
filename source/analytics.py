import asyncio
import json
from collections import OrderedDict
from datetime import timedelta, timezone, datetime
from itertools import product
from time import sleep

from extentions import logger  # noqa F401
from source.common import request, intervals, get_fee
from source.config import TICKERS, URL
from source.requests_input_data_makers import headers, make_candles_params
from utils import atimeit


def generate_request_params(count, figi, interval):
    now = datetime.now(tz=timezone(timedelta(0)))
    for i in range(count):
        then = now - timedelta(days=1)
        yield make_candles_params(interval, 'days', 1, figi, now=now, then=then)
        now = then


def subanalytics(ratios, ratio_max, ratio_min, profit_max, profit_min):
    return {
        # 'ratios': ratios,
        'ratio': {
            'max': ratio_max,
            'min': ratio_min
        },
        'profit': {
            'max': profit_max,
            'min': profit_min
        }
    }


def percentage_ratio(numerator, denominator):
    return abs(100 - numerator / denominator * 100)


def get_stock_analytics(candles, count=4):
    buying_ratios = []
    selling_ratios = []
    buying_profits = []
    selling_profits = []
    buying_keys = []
    selling_keys = []
    averages = []
    possible_profits = OrderedDict()

    max_profit = 0
    min_price = None
    max_price = None

    max_buying_ratio = None
    min_buying_ratio = None
    max_buying_profit = None
    min_buying_profit = None
    max_selling_ratio = None
    min_selling_ratio = None
    max_selling_profit = None
    min_selling_profit = None
    candles_lenght = 0

    for candle_buy, candle_sell in zip(candles[:-1], candles[1:]):
        buy = candle_buy['l']
        sell = candle_sell['h']
        average = (buy + candle_buy['h']) / 2
        selling_profit = sell - buy
        buying_profit = average - buy
        selling_ratio = percentage_ratio(sell, buy)
        buying_ratio = percentage_ratio(buy, average)

        if selling_ratio > 0 and buying_ratio > 0:
            fee = get_fee(buy, sell)
            pure_selling_profits = selling_profit - fee
            pure_selling_ratio = selling_ratio - pure_selling_profits * selling_ratio / selling_profit

            if selling_ratio > 0.05 and pure_selling_profits > 0:
                max_profit += pure_selling_profits
                selling_profit = pure_selling_profits
                selling_ratio = pure_selling_ratio

                if not min_price or min_price > buy:
                    min_price = buy
                elif not max_price or max_price < sell:
                    max_price = sell

                averages.append(average)
                buying_ratios.append(buying_profit)
                selling_ratios.append(selling_ratio)
                buying_profits.append(buying_profit)
                selling_profits.append(selling_profit)

                if not max_buying_ratio or max_buying_ratio < buying_ratio:
                    max_buying_ratio = buying_ratio
                elif not min_buying_ratio or min_buying_ratio > buying_ratio:
                    min_buying_ratio = buying_ratio
                if not max_buying_profit or max_buying_profit < buying_profit:
                    max_buying_profit = buying_profit
                elif not min_buying_profit or min_buying_profit > buying_profit:
                    min_buying_profit = buying_profit
                if not max_selling_ratio or max_selling_ratio < selling_ratio:
                    max_selling_ratio = selling_ratio
                elif not min_selling_ratio or min_selling_ratio > selling_ratio:
                    min_selling_ratio = selling_ratio
                if not max_selling_profit or max_selling_profit < selling_profit:
                    max_selling_profit = selling_profit
                elif not min_selling_profit or min_selling_profit > selling_profit:
                    min_selling_profit = selling_profit
                candles_lenght += 1

    average = sum(averages) / candles_lenght

    buying_step = (max_buying_ratio - min_buying_ratio) / count
    selling_step = (max_selling_ratio - min_selling_ratio) / count
    for k in range(count + 1):
        buying_key = min_buying_ratio + buying_step * k
        selling_key = min_selling_ratio + selling_step * k
        buying_keys.append(buying_key)
        selling_keys.append(selling_key)
    keys_products = list(map(lambda tuple_: (tuple_[1], tuple_[0]), product(selling_keys, buying_keys)))
    for buying_key, selling_key in keys_products:
        possible_profits[f'{buying_key}, {selling_key}'] = 0
    for buying_ratio, buying_profit, selling_ratio, selling_profit, average in \
            zip(buying_ratios, buying_profits, selling_ratios, selling_profits, averages):
        for buying_key, selling_key in keys_products:
            if buying_ratio >= buying_key and selling_ratio >= selling_key:
                possible_profit = selling_key * selling_profit / selling_ratio
                if possible_profit < 0:
                    raise Exception('possible_profit is less than I expected')
                possible_profits[f'{buying_key}, {selling_key}'] += possible_profit
    max_possible_profit_key = max(possible_profits, key=possible_profits.get)
    buying_key, selling_key = tuple(map(float, max_possible_profit_key.split(',')))
    max_possible_profit_tuple = (possible_profits[max_possible_profit_key], buying_key, selling_key)

    return {
        'max_possible_profit': max_possible_profit_tuple,
        'possible_profits': possible_profits,
        'buying': subanalytics(buying_ratios,
                               max_buying_ratio,
                               min_buying_ratio,
                               max_buying_profit,
                               min_buying_profit),
        'selling': subanalytics(selling_ratios,
                                max_selling_ratio,
                                min_selling_ratio,
                                max_selling_profit,
                                min_selling_profit),
        'min_price': min_price,
        'max_price': max_price,
        'max_profit': max_profit,
        'average': average
    }


async def get_stock_candles(ticker, figi, interval):
    url = URL + 'market/candles'
    candles = []
    tasks = [request(url, headers, get_stock_candles.__name__, params=params, ticker=ticker)
             for params in generate_request_params(30, figi, interval)]
    responses_data = await asyncio.gather(*tasks)
    for response_data in responses_data:
        candles += response_data['payload']['candles']
    return ticker, interval, candles


@atimeit
async def get_analytics(figies):
    max_possible_profits = {}
    max_possible_profits_dict = {}
    analytics_dict = {ticker: {} for ticker in TICKERS}
    ticker_interval_tuples = list(product(TICKERS, intervals))
    ticker_interval_tuples_length = len(ticker_interval_tuples)
    ticker_interval_tuples_length = ticker_interval_tuples_length // 4 + ticker_interval_tuples_length % 4

    for offset in range(ticker_interval_tuples_length):
        start = datetime.now()
        tasks = [get_stock_candles(ticker, figies[ticker], interval)
                 for ticker, interval in ticker_interval_tuples[offset*4:offset*4+4]]
        results = await asyncio.gather(*tasks)
        for ticker, interval, candles in results:
            analytics = get_stock_analytics(candles)
            # logger.info(f'{ticker}, {interval}: \n{pformat(analytics)}')
            analytics_dict[ticker][interval] = analytics
            curr_max_possible_profit_tuple = analytics['max_possible_profit']
            curr_max_possible_profit = curr_max_possible_profit_tuple[0]
            if ticker not in max_possible_profits_dict or max_possible_profits_dict[ticker] < curr_max_possible_profit:
                max_possible_profits_dict[ticker] = curr_max_possible_profit
                max_possible_profit_tuple = (interval, figies[ticker]) + curr_max_possible_profit_tuple
                max_possible_profits[ticker] = max_possible_profit_tuple
        end = datetime.now() - start
        delay = 60 - end.total_seconds()
        if delay > 0 and offset + 1 != ticker_interval_tuples_length:
            sleep(delay)
    with open('analytics.json', 'w') as file:
        json.dump(analytics_dict, file)
    return sorted(list(map(lambda el: (el[1][1],) + (el[0],) + (el[1][0],) + el[1][2:], max_possible_profits.items())),
                  key=lambda el: el[2], reverse=True)
