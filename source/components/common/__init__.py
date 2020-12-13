from enum import Enum
from functools import wraps

intervals = ['hour', '30min', '15min', '10min', '5min', '3min', '1min']
intervals_vals_dict = {'hour': 61, '30min': 31, '15min': 16, '10min': 11, '5min': 6, '3min': 4, '1min': 2}
# intervals = ['hour']


def get_fee(buying_price, selling_price):
    fee = + buying_price * 0.0005 + selling_price * 0.0005
    tax = (selling_price - buying_price - fee) * 0.13
    return fee + tax


class RequestsCountConstraintsNames(str, Enum):
    sandbox = '/sandbox'
    portfolio = '/portfolio'
    market = '/market'
    orders = '/orders'
    orders_limit_order = '/orders/limit-order'
    orders_market_order = '/orders/market-order'
    orders_cancel = '/orders/cancel'
    operations = '/operations'


REQUESTS_COUNT_CONSTRAINTS = {
    RequestsCountConstraintsNames.sandbox: 120,
    RequestsCountConstraintsNames.portfolio: 120,
    RequestsCountConstraintsNames.market: 120,
    RequestsCountConstraintsNames.orders: 100,
    RequestsCountConstraintsNames.orders_limit_order: 50,
    RequestsCountConstraintsNames.orders_market_order: 50,
    RequestsCountConstraintsNames.orders_cancel: 50,
    RequestsCountConstraintsNames.operations: 120
}


def limit(limit: RequestsCountConstraintsNames):
    def decorator(request_fn):
        @wraps
        def wrapper(*args):
            await request_fn(*args)
        return wrapper
    return decorator
