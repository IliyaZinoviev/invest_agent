import os

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.environ.get('ENVIRONMENT')
if ENVIRONMENT:
    ENVIRONMENT = ENVIRONMENT.upper()


class DBConfig:
    def __init__(self):
        self.DB_USERNAME = os.getenv('DB_USERNAME')
        assert self.DB_USERNAME, 'Env var is absent'
        self.DB_NAME = os.getenv('DB_NAME')
        assert self.DB_NAME, 'Env var is absent'
        self.DB_HOST = os.getenv('DB_HOST')
        assert self.DB_HOST, 'Env var is absent'
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        assert self.DB_PASSWORD, 'Env var is absent'
        self.DB_URL = f'postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}'


class Config(DBConfig):
    def __init__(self):
        super().__init__()
        self.SANDBOX_TOKEN = os.getenv('SANDBOX_TOKEN')
        assert self.SANDBOX_TOKEN, 'Env var is absent'
        self.PROD_TOKEN = os.getenv('PROD_TOKEN')
        assert self.PROD_TOKEN, 'Env var is absent'
        self.PROD_BROKER_ACC_ID = os.getenv('PROD_BROKER_ACC_ID')
        assert self.PROD_BROKER_ACC_ID, 'Env var is absent'
        self.SANDBOX_BROKER_ACC_ID = os.getenv('SANDBOX_BROKER_ACC_ID')
        assert self.SANDBOX_BROKER_ACC_ID, 'Env var is absent'
        self.TICKERS = os.getenv('TICKERS').split(',')
        assert self.TICKERS, 'Env var is absent'

        self.SANDBOX_URL = 'https://api-invest.tinkoff.ru/openapi/sandbox/'
        self.PROD_URL = 'https://api-invest.tinkoff.ru/openapi/'
        self.SOCKET_URL = 'wss://api-invest.tinkoff.ru/openapi/md/v1/md-openapi/ws'

        self.HEROKU_ENV = os.getenv('HEROKU_ENV', False)
        if not self.HEROKU_ENV:
            self.IS_SANDBOX_MODE = input('Do you want the sandbox mode monitoring [yn]? ')
            assert self.IS_SANDBOX_MODE in ['y', 'n'], 'Only "y", "n" vals are available!'
            self.IS_SANDBOX_MODE = self.IS_SANDBOX_MODE == 'y'
        else:
            self.IS_SANDBOX_MODE = True

        self.TOKEN = self.SANDBOX_TOKEN if self.IS_SANDBOX_MODE else self.PROD_TOKEN
        self.URL = self.SANDBOX_URL if self.IS_SANDBOX_MODE else self.PROD_URL
        self.BROKER_ACC_ID = self.SANDBOX_BROKER_ACC_ID if self.IS_SANDBOX_MODE else self.PROD_BROKER_ACC_ID


config = Config() if ENVIRONMENT != 'MIGRATION' else DBConfig()
