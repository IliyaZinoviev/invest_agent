import asyncio

from components.analytics.request_input_data_makers import generate_request_params
from components.common.request_handlers import request
from core.config import config
from components.common.request_input_data_makers import headers


async def get_stock_candles(ticker, figi, interval):
    url = config.URL + 'market/candles'
    candles = []
    tasks = [request(url, headers, get_stock_candles.__name__, params=params, ticker=ticker)
             for params in generate_request_params(30, figi, interval)]
    responses_data = await asyncio.gather(*tasks)
    for response_data in responses_data:
        candles += response_data['payload']['candles']
    return ticker, interval, candles
