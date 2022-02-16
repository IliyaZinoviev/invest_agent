from pydantic import Field

from components.common.enums import OperationEnum, IntervalEnum
from type_aliases import Figi
from serializers.base import AliasModel


class OperationsReq(AliasModel):
    figi: Figi | None
    to: str
    from_: str = Field(alias='from')


class LimitOrderReq(AliasModel):
    lots: int
    operation: OperationEnum
    price: float
    figi: str


class CancelOrderReq(AliasModel):
    id_: str = Field(alias='orderId')


class CandlesReq(AliasModel):
    figi: str
    to: str
    from_: str = Field(alias='from')
    interval: IntervalEnum
