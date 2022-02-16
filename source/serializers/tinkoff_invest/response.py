from pydantic import Field

from serializers.base import AliasModel
from serializers.tinkoff_invest.common import BaseOrder, Commission


class TinkoffInvestResp(AliasModel):
    tracking_id: str = Field(alias='trackingId')
    status: str
    payload: dict


class Error(AliasModel):
    message: str
    code: str


class LimitOrder(BaseOrder):
    status: str
    commission: Commission | None
    reject_reason: str | None = Field(alias='rejectReason')
