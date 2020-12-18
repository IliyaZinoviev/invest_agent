from source.config import URL
from source.extentions import session, logger
from source.requests_input_data_makers import make_search_by_ticker_params, params, headers


# intervals = ['hour', '30min', '15min', '10min', '5min', '3min', '1min']
intervals_vals_dict = {'hour': 61, '30min': 31, '15min': 16, '10min': 11, '5min': 6, '3min': 4, '1min': 2}
intervals = ['hour']


def get_fee(buying_price, selling_price):
    fee = + buying_price * 0.0005 + selling_price * 0.0005
    tax = (selling_price - buying_price - fee) * 0.13
    return fee + tax


async def request(url: str, headers: dict, fn_name: str, method: str = 'get', params: list = None, body: dict = None,
                  ticker: str = '') -> dict:
    async with getattr(session, method)(url, params=params, headers=headers, json=body) as response:
        response_code = response.status
        except_message = f'{fn_name}({ticker}): {response_code}, '
        if response_code in [429, 401]:
            raise Exception(except_message+f'{response.reason}')
        response_data = await response.json()
        if response_code == 200:
            return response_data
        raise Exception(f'{fn_name}({ticker}): {response_code}, {response_data}')


async def get_figi(ticker: str):
    params = make_search_by_ticker_params(ticker)
    url = URL + '/market/search/by-ticker'
    response_data = await request(url, headers, get_figi.__name__, params=params, ticker=ticker)
    return ticker, response_data['payload']['instruments'][0]['figi']


async def print_accounts():
    url = URL + 'user/accounts'
    response_data = await request(url, headers, print_accounts.__name__, params=params)
    logger.info(response_data['payload'])


async def print_portfolio():
    url = URL + 'portfolio'
    response_data = await request(url, headers, print_portfolio.__name__, params=params)
    logger.info(response_data['payload'])


async def print_currencies_portfolio():
    url = URL + 'portfolio/currencies'
    response_data = await request(url, headers, print_currencies_portfolio.__name__, params=params)
    logger.info(response_data['payload'])
