from utils.math import get_percentage_ratio

# intervals = ['hour', '30min', '15min', '10min', '5min', '3min', '1min']
intervals_vals_dict = {'hour': 61, '30min': 31, '15min': 16, '10min': 11, '5min': 6, '3min': 4, '1min': 2}
intervals = ['hour']


def get_fee(buying_price, selling_price):
    fee = + buying_price * 0.0005 + selling_price * 0.0005
    return fee + get_tax(selling_price - buying_price - fee)


def get_selling_price(price, count, profit):
    return get_percentage_ratio(profit / count, price) * price / 100 + price


def get_profit(price, count, selling_price):
    profit = (selling_price - price) * count
    return profit - get_tax(profit)


def get_tax(profit):
    return profit * 0.13
