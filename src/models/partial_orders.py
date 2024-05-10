from uuid import UUID

from pydantic import BaseModel

from enums import SalesChannel

__all__ = ('PartialOrder',)


class PartialOrder(BaseModel):
    id: UUID
    price: int
    number: str
    sales_channel: SalesChannel
    account_name: str
