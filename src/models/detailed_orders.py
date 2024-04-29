from datetime import datetime

from pydantic import computed_field

from models.partial_orders import PartialOrder

__all__ = ('DetailedOrder',)


class DetailedOrder(PartialOrder):
    unit_name: str
    created_at: datetime
    canceled_at: datetime
    receipt_printed_at: datetime | None
    courier_name: str | None
    canceled_by_user_name: str | None

    @computed_field
    def has_printed_receipt(self) -> bool:
        return self.receipt_printed_at is not None
