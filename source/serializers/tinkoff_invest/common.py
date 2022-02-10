from datetime import datetime
from decimal import Decimal

from pydantic import Field

from components.common.enums import CurrencyEnum, OperationEnum, OrderTypeEnum
from serializers.base import AliasModel


class Trade(AliasModel):
    trade_id: str = Field(alias='tradeId')
    date: datetime
    price: int
    quantity: int


class Commission(AliasModel):
    currency: CurrencyEnum
    value: Decimal


class Operation(AliasModel):
    id_: str = Field(alias='id')
    status: str
    trades: list[Trade] | None
    commission: Commission | None
    currency: str
    payment: int
    price: int
    quantity: int
    quantity_executed: int = Field(alias='quantityExecuted')
    figi: str
    instrument_type: str = Field(alias='instrumentType')
    is_margin_call: bool = Field(alias='isMarginCall')
    date: str
    operation_type: str = Field(alias='operationType')


class Operations(AliasModel):
    operations: list[Operation]


class Price(AliasModel):
    currency: str
    value: Decimal


class Position(AliasModel):
    figi: str
    ticker: str
    isin: str | None
    instrument_type: str = Field(alias='instrumentType')
    balance: Decimal
    blocked: Decimal | None
    expected_yield: Price = Field(alias='expectedYield')
    lots: int
    average_position_price: Price = Field(alias='averagePositionPrice')
    average_position_price_no_nkd: Price | None = Field(alias='averagePositionPriceNoNkd')
    name: str


class Portfolio(AliasModel):
    positions: list[Position]


class Currency(AliasModel):
    currency: CurrencyEnum
    balance: Decimal
    blocked: Decimal | None


class Currencies(AliasModel):
    currencies: list[Currency]


class Candle(AliasModel):
    figi: str
    interval: str
    o: Decimal
    c: Decimal
    h: Decimal
    l: Decimal
    v: int
    time: str


class Candles(AliasModel):
    figi: str
    interval: str
    candles: list[Candle]


class BaseOrder(AliasModel):
    id_: str = Field(alias='orderId')
    operation: OperationEnum
    requested_lots: int = Field(alias='requestedLots')
    executed_lots: int = Field(alias='executedLots')


class Order(BaseOrder):
    figi: str
    status: str
    price: float
    type: OrderTypeEnum


class Stock(AliasModel):
    figi: str
    ticker: str
    isin: str
    minPriceIncrement: Decimal | None
    lot: int
    currency: CurrencyEnum
    name: str
    type: str


class Stocks(AliasModel):
    instruments: list[Stock]


class OrderBookItem(AliasModel):
    price: Decimal
    quantity: int


class OrderBook(AliasModel):
    figi: str
    depth: int
    trade_status: str = Field(alias='tradeStatus')
    min_price_increment: Decimal = Field(alias='minPriceIncrement')
    last_price: Decimal = Field(alias='lastPrice')
    close_price: Decimal = Field(alias='closePrice')
    limit_up: Decimal | None = Field(alias='limitUp')
    limit_down: Decimal | None = Field(alias='limitDown')
    bids: list[OrderBookItem]
    asks: list[OrderBookItem]