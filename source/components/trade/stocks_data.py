import json
from operator import itemgetter

from core.config import TICKERS


def get_sorted_stocks() -> list:
    with open('../stocks.json', 'r') as file:
        stocks_data = json.load(file)
        filtered_stocks_data = {k: v for k, v in stocks_data.items() if k in TICKERS}
        stock_data_list = list(map(lambda el: {**{'ticker': el[0]}, **el[1]}, filtered_stocks_data.items()))
        return sorted(stock_data_list, key=itemgetter('possible_profit'), reverse=True)
