from collections import OrderedDict
from functools import partialmethod
from itertools import product

from round_utils import ceil

from components.common import get_fee
from utils.cond import is_less, is_more
from utils.math import get_step, get_proportions_left_nominator, get_average, get_percentage_ratio
from utils.struct import get_val_by_keys_seq


class StockAnalyzer:
    """
        Functions which are started with 'put' mean that they put something to 'stock_analytics' or 'stock_data' obj
    attribute.
        Functions which are started with 'update' mean that they update something in 'stock_analytics' obj attribute.
    """
    def __init__(self, candles, min_price_inc, step_count: int = 4):
        self.__init(candles, min_price_inc, step_count)
        self.__execute()

    def __build_subanalytics(self):
        return {
            # 'ratios': ratios,
            'ratio': {
                'max': None,
                'min': None
            },
            'profit': {
                'max': None,
                'min': None
            }
        }

    @staticmethod
    def __is_profitable(selling_ratio, pure_selling_profits) -> bool:
        return selling_ratio > 0.05 and pure_selling_profits > 0

    def __put_if_cond_fn(self, cond_fn, keys, val):
        key = keys[-1]
        struct = get_val_by_keys_seq(self.__stock_analytics, keys[:-1])
        if cond_fn(struct[key], val):
            struct[key] = val

    __put_if_less = partialmethod(__put_if_cond_fn, is_less)
    __put_if_more = partialmethod(__put_if_cond_fn, is_more)

    def __update_max_profit(self, profit):
        self.__stock_analytics['common_profit'] += profit

    __put_min_price = partialmethod(__put_if_less, ['min_price'])
    __put_max_price = partialmethod(__put_if_more, ['max_price'])

    def __put_if_min_or_put_if_max(self, keys, val):
        struct = get_val_by_keys_seq(self.__stock_analytics, keys)
        if is_less(struct['min'], val):
            struct['min'] = val
        elif is_more(struct['max'], val):
            struct['max'] = val

    __put_buying_ratio = partialmethod(__put_if_min_or_put_if_max, ['buying', 'ratio'])
    __put_buying_profit = partialmethod(__put_if_min_or_put_if_max, ['buying', 'profit'])
    __put_selling_ratio = partialmethod(__put_if_min_or_put_if_max, ['selling', 'ratio'])
    __put_selling_profit = partialmethod(__put_if_min_or_put_if_max, ['selling', 'profit'])

    def __closure_average_price_methods(self):
        significant_candles_length = 0
        averages = []

        def append_average(average):
            nonlocal significant_candles_length, averages
            significant_candles_length += 1
            averages.append(average)

        def put_average_price():
            nonlocal self, significant_candles_length, averages
            self.__stock_analytics['average_price'] = sum(averages) / significant_candles_length

        return append_average, put_average_price

    def __get_step(self, keys):
        struct = get_val_by_keys_seq(self.__stock_analytics, keys)
        return get_step(struct['max'], struct['min'], self.__steps_count)

    __get_buying_step = partialmethod(__get_step, ['buying', 'ratio'])
    __get_selling_step = partialmethod(__get_step, ['selling', 'ratio'])

    def __get_val_by_keys_seq(self, *keys_seq: [str]):
        return get_val_by_keys_seq(self.__stock_analytics, keys_seq)

    def __product_possible_buying_selling_ratios(self):
        possible_buying_ratios = []
        possible_selling_ratios = []
        buying_step = self.__get_buying_step()
        selling_step = self.__get_selling_step()
        for k in range(self.__steps_count + 1):
            possible_buying_ratio = self.__get_val_by_keys_seq('buying', 'ratio', 'min') + buying_step * k
            possible_selling_ratio = self.__get_val_by_keys_seq('selling', 'ratio', 'min') + selling_step * k
            possible_buying_ratios.append(possible_buying_ratio)
            possible_selling_ratios.append(possible_selling_ratio)
        return list(map(lambda tuple_: (tuple_[1], tuple_[0]),
                        product(possible_selling_ratios, possible_buying_ratios)))

    @staticmethod
    def __init_possible_profits(product_possible_buying_selling_ratios):
        possible_profits = OrderedDict()
        for possible_buying_ratio, possible_selling_ratio in product_possible_buying_selling_ratios:
            possible_profits[f'{possible_buying_ratio}, {possible_selling_ratio}'] = 0
        return possible_profits

    def __put_possible_profits(self, possible_profits):
        self.__stock_analytics['possible_profits'] = possible_profits

    def __find_max_possible_profit_and_ratios(self, product_possible_buying_selling_ratios: list,
                                              possible_profits: dict):
        for buying_ratio, selling_ratio, selling_profit in zip(self.__buying_ratios,
                                                               self.__selling_ratios,
                                                               self.__selling_profits):
            for possible_buying_ratio, possible_selling_ratio in product_possible_buying_selling_ratios:
                if buying_ratio >= possible_buying_ratio and selling_ratio >= possible_selling_ratio:
                    possible_profit = get_proportions_left_nominator(possible_selling_ratio, selling_profit,
                                                                     selling_ratio)
                    if possible_profit < 0:
                        raise Exception('possible_profit is less than I expected')
                    possible_profits[f'{possible_buying_ratio}, {possible_selling_ratio}'] += possible_profit
        max_possible_profit_key = max(possible_profits, key=possible_profits.get)
        max_possible_profit = possible_profits[max_possible_profit_key]
        return max_possible_profit_key, max_possible_profit

    def __put_max_possible_profit_to_stock_data(self, max_possible_profit_key: str, max_possible_profit_val: float):
        possible_buying_ratio, possible_selling_ratio = tuple(map(float, max_possible_profit_key.split(',')))
        self.__stock_data = {'possible_profit': max_possible_profit_val,
                             'buying_ratio': possible_buying_ratio,
                             'selling_ratio': possible_selling_ratio}

    def __put_max_possible_profit_to_stock_analytics(self,
                                                     max_possible_profit_key: str,
                                                     max_possible_profit_val: float):
        self.__stock_analytics['max_possible_profit'] = {max_possible_profit_key:
                                                         max_possible_profit_val}

    def __init(self, candles, min_price_inc, step_count):
        self.__stock_data = {
            'possible_profit': None,
            'buying_ratio': None,
            'selling_ratio': None
        }
        self.__stock_analytics = {
            'common_profit': 0,
            'max_possible_profit': {},
            'possible_profits': OrderedDict(),
            'buying': self.__build_subanalytics(),
            'selling': self.__build_subanalytics(),
            'min_price': None,
            'max_price': None,
            'average_price': None
        }
        self.__steps_count = step_count
        self.__candles = candles
        self.__min_price_inc = min_price_inc

        self.__buying_ratios = []
        self.__selling_ratios = []
        self.__buying_profits = []
        self.__selling_profits = []
        self.__append_average, self.__put_average_price = self.__closure_average_price_methods()

    def __execute(self):
        for candle_buy, candle_sell in zip(self.__candles[:-1], self.__candles[1:]):
            buy = candle_buy['l']
            sell = candle_sell['h']
            average = get_average(buy, sell)
            rounded_average = ceil(average, self.__min_price_inc)
            selling_ratio = get_percentage_ratio(sell, buy)
            buying_ratio = get_percentage_ratio(buy, rounded_average)
            selling_profit = sell - buy
            buying_profit = rounded_average - buy
            if selling_ratio == 0 and buying_ratio == 0:
                continue
            fee = get_fee(buy, sell)
            pure_selling_profits = selling_profit - fee
            if self.__is_profitable(selling_ratio, pure_selling_profits):
                pure_selling_ratio = get_proportions_left_nominator(pure_selling_profits, selling_ratio, selling_profit)
                self.__update_max_profit(pure_selling_profits)
                self.__put_min_price(buy)
                self.__put_max_price(sell)
                self.__put_buying_ratio(buying_ratio)
                self.__put_buying_profit(buying_profit)
                self.__put_selling_ratio(selling_ratio)
                self.__put_selling_profit(selling_profit)
                self.__append_average(average)
                self.__buying_ratios.append(buying_profit)
                self.__buying_profits.append(buying_profit)
                self.__selling_ratios.append(pure_selling_ratio)
                self.__selling_profits.append(pure_selling_profits)
        self.__put_average_price()
        product_possible_buying_selling_ratios = self.__product_possible_buying_selling_ratios()
        possible_profits = self.__init_possible_profits(product_possible_buying_selling_ratios)
        self.__put_possible_profits(possible_profits)
        max_possible_profit_key, max_possible_profit = self.__find_max_possible_profit_and_ratios(
            product_possible_buying_selling_ratios, possible_profits)
        self.__put_max_possible_profit_to_stock_data(max_possible_profit_key, max_possible_profit)
        self.__put_max_possible_profit_to_stock_analytics(max_possible_profit_key, max_possible_profit)

    @property
    def stock_analytics(self):
        return self.__stock_analytics

    @property
    def stock_data(self):
        return self.__stock_data
