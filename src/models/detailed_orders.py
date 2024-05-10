from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, computed_field

from enums import SalesChannel

__all__ = ('DetailedOrder',)


class DetailedOrder(BaseModel):
    id: UUID
    price: int
    number: str
    sales_channel: SalesChannel
    unit_name: str
    created_at: datetime
    canceled_at: datetime
    receipt_printed_at: datetime | None
    courier_name: str | None
    canceled_by_user_name: str | None

    @computed_field
    def has_printed_receipt(self) -> bool:
        return self.receipt_printed_at is not None
