import logging

from source.config import SANDBOX_TOKEN, MARKET_URL, SANDBOX_URL
from source.extentions import session
from source.requests_makers import make_search_by_ticker_params, params, headers


async def request(url: str, headers: dict, params: list, fn_name: str, method: str = 'get', body: dict = None,
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
    url = MARKET_URL + '/market/search/by-ticker'
    response_data = await request(url, headers, params, get_figi.__name__, ticker=ticker)
    return ticker, response_data['payload']['instruments'][0]['figi']


async def auth():
    headers = {'Authorization': f'Bearer {SANDBOX_TOKEN}'}
    body = {'brokerAccountType': 'Tinkoff'}
    url = SANDBOX_URL + 'sandbox/register'
    await request(url, headers, params, auth.__name__, method='post', body=body)


async def print_accounts():
    url = MARKET_URL + 'user/accounts'
    response_data = await request(url, headers, params, print_accounts.__name__)
    logging.info(response_data['payload'])
