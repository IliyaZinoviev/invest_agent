from datetime import timedelta, timezone, datetime
from components.common.request_input_data_makers import make_candles_params


def generate_request_params(count, figi, interval):
    now = datetime.now(tz=timezone(timedelta(0)))
    for i in range(count):
        then = now - timedelta(days=1)
        yield make_candles_params(interval, 'days', 1, figi, now=now, then=then)
        now = then
