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
