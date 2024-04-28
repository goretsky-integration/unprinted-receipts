from datetime import datetime

from models.partial_orders import PartialOrder

__all__ = ('DetailedOrder',)


class DetailedOrder(PartialOrder):
    unit_name: str
    created_at: datetime
    canceled_at: datetime
    receipt_printed_at: datetime | None
    courier_name: str | None
    canceled_by_user_name: str | None
