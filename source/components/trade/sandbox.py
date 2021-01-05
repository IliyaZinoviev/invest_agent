from components.common.request_handlers import request
from core.config import config
from core.extentions import logger


async def register():
    headers = {'Authorization': f'Bearer {config.SANDBOX_TOKEN}'}
    body = {'brokerAccountType': 'TinkoffIis'}
    url = config.SANDBOX_URL + 'sandbox/register'
    response_data = await request(url, headers, register.__name__, method='post', body=body)
    logger.info(response_data)


async def set_currencies_balance(currency, balance):
    headers = {'Authorization': f'Bearer {config.SANDBOX_TOKEN}'}
    params = [('brokerAccountId', config.SANDBOX_BROKER_ACC_ID)]
    body = {'brokerAccountType': 'TinkoffIis',
            'currency': currency,
            'balance': balance}
    url = config.SANDBOX_URL + 'sandbox/currencies/balance'
    response_data = await request(url, headers, set_currencies_balance.__name__,
                                  method='post',
                                  params=params,
                                  body=body)
    logger.info(response_data)


async def clear_sandbox_portfolio():
    headers = {'Authorization': f'Bearer {config.SANDBOX_TOKEN}'}
    params = [('brokerAccountId', config.SANDBOX_BROKER_ACC_ID)]
    url = config.SANDBOX_URL + 'sandbox/clear'
    response_data = await request(url, headers, register.__name__, method='post', params=params)
    logger.info(response_data)
