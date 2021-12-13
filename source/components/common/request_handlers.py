import asyncio
from typing import Callable, Any

from source.components.common import intervals_vals_dict
from source.components.common.exceptions import ExternalMarketError
from source.components.common.request_input_data_makers import make_search_by_ticker_params, headers, params, \
    make_candles_params, make_orderbook_params
from source.components.serializers import StocksResponse, OrderbookResponse, Stock
from source.core.config import config
from source.core.extentions import session_provider, logger


async def request(url: str, headers: dict, fn_name: str, method: str = 'get', params: list = None, body: dict = None,
                  ticker: str = '') -> dict:
    async with getattr(session_provider[0], method)(url, params=params, headers=headers, json=body) as response:
        response_code = response.status
        except_message = f'{fn_name}({ticker}): {response_code}, '
        if response_code in [429, 401]:
            raise ExternalMarketError(
                msg=f'{except_message} {response.reason}',
                detail=response.reason,
                code=response_code,
                ticker=ticker)
        response_data = await response.json()
        if response_code == 200:
            return response_data
        raise ExternalMarketError(msg=f'{fn_name}({ticker}): {response_code}, {response_data}',
                                  detail=response_data,
                                  code=response_code,
                                  ticker=ticker)


async def get_figi_and_min_price_inc(ticker: str):
    params = make_search_by_ticker_params(ticker)
    url = config.URL + '/market/search/by-ticker'
    response_data = await request(url, headers, get_figi_and_min_price_inc.__name__, params=params, ticker=ticker)
    figi = response_data['payload']['instruments'][0]['figi']
    min_price_increment = response_data['payload']['instruments'][0]['minPriceIncrement']
    return ticker, figi, min_price_increment


async def get_figi(ticker: str):
    params = make_search_by_ticker_params(ticker)
    url = config.URL + '/market/search/by-ticker'
    response_data = await request(url, headers, get_figi_and_min_price_inc.__name__, params=params, ticker=ticker)
    res = response_data
    return res


async def print_accounts():
    url = config.URL + 'user/accounts'
    response_data = await request(url, headers, print_accounts.__name__, params=params)
    logger.info(response_data['payload'])


async def print_portfolio():
    url = config.URL + 'portfolio'
    response_data = await request(url, headers, print_portfolio.__name__, params=params)
    logger.info(response_data['payload'])


async def print_currencies_portfolio():
    url = config.URL + 'portfolio/currencies'
    response_data = await request(url, headers, print_currencies_portfolio.__name__, params=params)
    logger.info(response_data['payload'])


async def get_stocks() -> StocksResponse:
    url = config.URL + 'market/stocks'
    res = await request(url, headers, get_stocks.__name__)
    return StocksResponse(**res)


async def get_figies_and_min_price_incs(tickers: list[str]):
    tasks = [get_figi_and_min_price_inc(ticker) for ticker in tickers]
    result = await asyncio.gather(*tasks)
    figies = {ticker: figi for ticker, figi, _ in result}
    min_price_incs = {ticker: float(min_price_inc_str) for ticker, _, min_price_inc_str in result}
    return figies, min_price_incs


async def get_candles(figi: str, ticker: str, interval: str):
    url = config.URL + 'market/candles'
    params = make_candles_params(interval, 'minutes', intervals_vals_dict[interval], figi)
    response_data = await request(url, headers, get_candles.__name__, params=params, ticker=ticker)
    candles = response_data
    return candles


async def get_orderbook(stock: Stock, depth: int) -> tuple[OrderbookResponse, Stock]:
    url = config.URL + 'market/orderbook'
    params = make_orderbook_params(stock.figi, depth)
    response_data = await request(url, headers, get_orderbook.__name__, params=params, ticker=stock.ticker)
    return OrderbookResponse(**response_data), stock
