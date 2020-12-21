import os

from dotenv import load_dotenv
load_dotenv()

SANDBOX_TOKEN = os.getenv('SANDBOX_TOKEN')
assert SANDBOX_TOKEN, 'Env var is absent'
PROD_TOKEN = os.getenv('PROD_TOKEN')
assert PROD_TOKEN, 'Env var is absent'
PROD_BROKER_ACC_ID = os.getenv('PROD_BROKER_ACC_ID')
assert PROD_BROKER_ACC_ID, 'Env var is absent'
SANDBOX_BROKER_ACC_ID = os.getenv('SANDBOX_BROKER_ACC_ID')
assert SANDBOX_BROKER_ACC_ID, 'Env var is absent'
TICKERS = os.getenv('TICKERS').split(',')
assert TICKERS, 'Env var is absent'


SANDBOX_URL = 'https://api-invest.tinkoff.ru/openapi/sandbox/'
PROD_URL = 'https://api-invest.tinkoff.ru/openapi/'
SOCKET_URL = 'wss://api-invest.tinkoff.ru/openapi/md/v1/md-openapi/ws'

IS_SANDBOX_MODE = input('Do you want the sandbox mode monitoring [yn]? ')
assert IS_SANDBOX_MODE in ['y', 'n'], 'Only "y", "n" vals are available!'
IS_SANDBOX_MODE = IS_SANDBOX_MODE == 'y'

TOKEN = SANDBOX_TOKEN if IS_SANDBOX_MODE else PROD_TOKEN
URL = SANDBOX_URL if IS_SANDBOX_MODE else PROD_URL
BROKER_ACC_ID = SANDBOX_BROKER_ACC_ID if IS_SANDBOX_MODE else PROD_BROKER_ACC_ID
