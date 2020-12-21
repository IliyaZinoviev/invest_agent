from datetime import timezone, timedelta, datetime

from core.config import BROKER_ACC_ID, TOKEN

broker_acc_id_param = ('brokerAccountId', BROKER_ACC_ID)
headers = {'Authorization': f'Bearer {TOKEN}'}
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


def make_limit_order_body(operation: str, price: float, lots: int = 1):
    return {'lots': lots, 'operation': operation, 'price': price}


def make_search_by_ticker_params(ticker: str):
    return [('ticker', ticker)]
