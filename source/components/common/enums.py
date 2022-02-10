from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class CurrencyEnum(StrEnum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'


class AccEnum(StrEnum):
    IIS = 'IIS'
    BROKER = 'BROKER'


class OperationEnum(StrEnum):
    BUY = 'Buy'
    SELL = 'Sell'


class OrderTypeEnum(StrEnum):
    LIMIT = 'Limit'
    MARKET = 'Market'


class IntervalEnum(StrEnum):
    D1MIN = '1min'
    D2MIN = '2min'
    D3MIN = '3min'
    D5MIN = '5min'
    D10MIN = '10min'
    D15MIN = '15min'
    D30MIN = '30min'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'


class TariffEnum(StrEnum):
    TRADER = 'TRADER'
    INVESTOR = 'INVESTOR'
