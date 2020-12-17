import json
from collections import OrderedDict
from datetime import timedelta, timezone, datetime
from itertools import product
from pprint import pprint
from time import sleep

from source.config import TICKERS, MARKET_URL
from source.extentions import session
from source.requests_makers import headers

intervals = ['hour', '30min', '15min', '10min', '5min', '3min', '1min']

counter = 0


def percentage_ratio(numerator, denominator):
    return abs(100 - numerator / denominator * 100)


def get_stock_analytics(candles):
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
            tax = selling_profit * 0.13
            fee = + (buying_profit / buying_ratio * 0.05) + (selling_profit / selling_ratio) * 0.05
            pure_selling_profits = selling_profit - (fee + tax)
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

    count = 4
    buying_step = (max_buying_ratio - min_buying_ratio) / count
    selling_step = (max_selling_ratio - min_selling_ratio) / count
    for k in range(count + 1):
        buying_key = min_buying_ratio + buying_step * k
        selling_key = min_selling_ratio + selling_step * k
        buying_keys.append(buying_key)
        selling_keys.append(selling_key)
    keys_products = list(map(lambda tuple_: (tuple_[1], tuple_[0]), product(selling_keys, buying_keys)))
    for buying_key, selling_key in keys_products:
        possible_profits[str((buying_key, selling_key))] = 0
    for buying_ratio, buying_profit, selling_ratio, selling_profit, average in \
            zip(buying_ratios, buying_profits, selling_ratios, selling_profits, averages):
        for buying_key, selling_key in keys_products:
            if buying_ratio >= buying_key and selling_ratio >= selling_key:
                possible_profit = selling_key * selling_profit / selling_ratio
                if possible_profit < 0:
                    raise Exception('possible_profit is less than I expected')
                possible_profits[str((buying_key, selling_key))] += possible_profit

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

    return {
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
    global counter
    counter += 1
    if counter == 4:
        counter = 0
        sleep(60)
    candles = []
    now = datetime.now(tz=timezone(timedelta(0))) - timedelta(days=1)
    for i in range(30):
        then = now - timedelta(days=1)
        params = [('figi', figi),
                  ('from', then.isoformat()),
                  ('to', now.isoformat()),
                  ('interval', interval)]
        async with session.get(MARKET_URL + 'market/candles',
                               params=params,
                               headers=headers) as response:
            response_data = await response.json()
            candles += response_data['payload']['candles']
            now = then
    return candles


async def get_analytics(figies):
    analytics_list = {}
    async with session:
        for ticker, interval in product(TICKERS, intervals):
            candles = await get_stock_candles(ticker, figies[ticker], interval)
            print(ticker, interval)
            analytics = get_stock_analytics(candles)
            pprint(analytics)
            analytics_list[f'{ticker}, {interval}'] = analytics
    with open('analytics.json', 'w') as file:
        json.dump(analytics_list, file)
