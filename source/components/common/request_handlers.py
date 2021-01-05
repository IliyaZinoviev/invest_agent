import asyncio

from core.config import config
from core.extentions import logger, session_provider
from components.common.request_input_data_makers import make_search_by_ticker_params, params, headers


async def request(url: str, headers: dict, fn_name: str, method: str = 'get', params: list = None, body: dict = None,
                  ticker: str = '') -> dict:
    async with getattr(session_provider[0], method)(url, params=params, headers=headers, json=body) as response:
        response_code = response.status
        except_message = f'{fn_name}({ticker}): {response_code}, '
        if response_code in [429, 401]:
            raise Exception(except_message+f'{response.reason}')
        response_data = await response.json()
        if response_code == 200:
            return response_data
        raise Exception(f'{fn_name}({ticker}): {response_code}, {response_data}')


async def get_figi_and_min_price_inc(ticker: str):
    params = make_search_by_ticker_params(ticker)
    url = config.URL + '/market/search/by-ticker'
    response_data = await request(url, headers, get_figi_and_min_price_inc.__name__, params=params, ticker=ticker)
    figi = response_data['payload']['instruments'][0]['figi']
    min_price_increment = response_data['payload']['instruments'][0]['minPriceIncrement']
    return ticker, figi, min_price_increment


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


async def get_figies_and_min_price_incs():
    tasks = [get_figi_and_min_price_inc(ticker) for ticker in config.TICKERS]
    result = await asyncio.gather(*tasks)
    figies = {ticker: figi for ticker, figi, _ in result}
    min_price_incs = {ticker: float(min_price_inc_str) for ticker, _, min_price_inc_str in result}
    return figies, min_price_incs
