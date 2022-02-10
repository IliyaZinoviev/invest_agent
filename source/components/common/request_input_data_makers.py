from datetime import datetime, timedelta, timezone
from decimal import Decimal

from source.app.config import config

broker_acc_id_param = ('brokerAccountId', config.BROKER_ACC_ID)
headers = {'Authorization': f'Bearer {config.TOKEN}'}
params = [broker_acc_id_param]


def make_candles_params(interval: str, interval_key: str, interval_val: int, figi: str, now=None, then=None):
    if not now:
        now = datetime.now(tz=timezone(timedelta(0)))
    if not then:
        then = now - timedelta(**{interval_key: interval_val})
    return [('figi', figi),
            ('from', then.isoformat()),
            ('to', now.isoformat()),
            ('interval', interval)]


def make_limit_order_params(figi: str):
    return [('figi', figi), broker_acc_id_param]


def make_limit_order_body(operation: str, price: Decimal, lots: int = 1):
    return {'lots': lots, 'operation': operation, 'price': float(price)}


def make_search_by_ticker_params(ticker: str):
    return [('ticker', ticker)]


def make_orderbook_params(figi: str, depth: int):
    return {'figi': figi, 'depth': depth}
