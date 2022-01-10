from decimal import Decimal

# intervals = ['hour', '30min', '15min', '10min', '5min', '3min', '1min']
from source.utils.math import get_percentage_ratio

intervals_vals_dict = {'hour': 61, '30min': 31, '15min': 16, '10min': 11, '5min': 6, '3min': 4, '1min': 2}
intervals = ['hour']


def get_commission(price) -> float:
    return price * 0.0005


def get_fee(buying_price, selling_price):
    fee = get_commission(buying_price) + get_commission(selling_price)
    return fee + get_tax(selling_price - buying_price - fee)


def get_selling_price(price, count, profit):
    return get_percentage_ratio(profit / count, price) * price / 100 + price


def get_profit(price, count, selling_price):
    profit = (selling_price - price) * count
    return profit - get_tax(profit)


def get_tax(profit):
    return profit * 0.13


def inc_funds(funds, min_p, max_p):
    fund = funds[-1]
    count = fund // min_p
    commission = get_commission(count * min_p)
    profit = (count * max_p) - (fund - (fund % count)) - commission
    funds.append(fund + profit)
    return funds[-1]


def get_tariff_for_month(money: Decimal):
    investor = money * Decimal('0.003')
    trader = money * Decimal('0.05') + Decimal('290')
    if investor <= trader:
        return 'investor'
    else:
        return 'trader'
