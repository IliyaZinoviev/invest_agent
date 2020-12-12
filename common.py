import logging
from aiohttp import ClientSession

from config import BROKER_ACC_ID, MARKET_TOKEN, SANDBOX_TOKEN

sandbox_url = 'https://api-invest.tinkoff.ru/openapi/sandbox/'
market_url = 'https://api-invest.tinkoff.ru/openapi/'
socket_url = 'wss://api-invest.tinkoff.ru/openapi/md/v1/md-openapi/ws'

broker_acc_id_param = ('brokerAccountId', BROKER_ACC_ID)
headers = {'Authorization': f'Bearer {MARKET_TOKEN}'}
price_percentage_ratio_for_purchase = 3  # TODO add formula for it
price_percentage_ratio_for_sell = 0  # TODO add formula for it


async def get_figi(session, ticker):
    headers = {'Authorization': f'Bearer {MARKET_TOKEN}'}
    async with session.get(market_url + f'/market/search/by-ticker?ticker={ticker}',
                           headers=headers) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'get_figi({ticker}): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            return ticker, response_data['payload']['instruments'][0]['figi']
        else:
            raise Exception(f'get_figi({ticker}): {resp_code}, {response_data}')


async def auth(session):
    body = {'brokerAccountType': 'Tinkoff'}
    headers = {'Authorization': f'Bearer {SANDBOX_TOKEN}'}
    async with session.post(sandbox_url+'sandbox/register',
                            headers=headers,
                            json=body) as _:
        pass


async def print_accounts(session: ClientSession):
    async with session.get(market_url + 'user/accounts',
                           headers=headers) as response:
        resp_code = response.status
        if resp_code in [429, 401]:
            raise Exception(f'print_accounts(): {resp_code}, {response.reason}')
        response_data = await response.json()
        if resp_code == 200:
            logging.info(response_data['payload'])
        else:
            raise Exception(f'print_accounts(): {resp_code}, {response_data}')
