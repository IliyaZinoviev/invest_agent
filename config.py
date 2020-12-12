import os

from dotenv import load_dotenv
load_dotenv()

SANDBOX_TOKEN = os.getenv('SANDBOX_TOKEN')
assert SANDBOX_TOKEN, 'Env var is absent'
MARKET_TOKEN = os.getenv('MARKET_TOKEN')
assert MARKET_TOKEN, 'Env var is absent'
BROKER_ACC_ID = os.getenv('BROKER_ACC_ID')
assert BROKER_ACC_ID, 'Env var is absent'
TICKERS = os.getenv('TICKERS').split(',')
assert TICKERS, 'Env var is absent'
