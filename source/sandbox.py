from source.common import request
from source.config import SANDBOX_TOKEN, SANDBOX_URL, SANDBOX_BROKER_ACC_ID
from source.extentions import logger


async def register():
    headers = {'Authorization': f'Bearer {SANDBOX_TOKEN}'}
    body = {'brokerAccountType': 'TinkoffIis'}
    url = SANDBOX_URL + 'sandbox/register'
    response_data = await request(url, headers, register.__name__, method='post', body=body)
    logger.info(response_data)


async def set_currencies_balance():
    headers = {'Authorization': f'Bearer {SANDBOX_TOKEN}'}
    params = [('brokerAccountId', SANDBOX_BROKER_ACC_ID)]
    body = {'brokerAccountType': 'TinkoffIis',
            'currency': 'USD',
            'balance': 1000}
    url = SANDBOX_URL + 'sandbox/currencies/balance'
    await request(url, headers, set_currencies_balance.__name__, method='post', params=params, body=body)


async def clear_sandbox_portfolio():
    headers = {'Authorization': f'Bearer {SANDBOX_TOKEN}'}
    params = [('brokerAccountId', SANDBOX_BROKER_ACC_ID)]
    url = SANDBOX_URL + 'sandbox/clear'
    response_data = await request(url, headers, register.__name__, method='post', params=params)
    logger.info(response_data)
