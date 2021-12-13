from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Stock(BaseModel):
    figi: str
    ticker: str
    isin: str
    minPriceIncrement: Optional[Decimal]
    lot: int
    currency: str
    name: str
    type: str


class StocksResponsePayload(BaseModel):
    instruments: list[Stock]


class StocksResponse(BaseModel):
    payload: StocksResponsePayload


class OrderBookItem(BaseModel):
    price: Decimal
    quantity: int


class OrderBookResponsePayload(BaseModel):
    figi: str
    depth: int
    tradeStatus: str
    minPriceIncrement: Decimal
    lastPrice: Decimal
    closePrice: Decimal
    limitUp: Optional[Decimal]
    limitDown: Optional[Decimal]
    bids: list[OrderBookItem]
    asks: list[OrderBookItem]


class OrderbookResponse(BaseModel):
    payload: OrderBookResponsePayload
