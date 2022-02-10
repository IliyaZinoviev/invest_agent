import asyncio

from source.components.analytics.request_input_data_makers import generate_request_params
from source.components.common.request_handlers import request
from source.components.common.request_input_data_makers import headers
from source.app.config import config


async def get_stock_candles(ticker, figi, interval):
    url = config.BASE_URL + 'market/candles'
    candles = []
    tasks = [request(url, headers, get_stock_candles.__name__, params=params, ticker=ticker)
             for params in generate_request_params(30, figi, interval)]
    responses_data = await asyncio.gather(*tasks)
    for response_data in responses_data:
        candles += response_data['payload']['candles']
    return ticker, interval, candles
