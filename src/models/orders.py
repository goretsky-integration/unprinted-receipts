from uuid import UUID

from pydantic import BaseModel

__all__ = ('Order',)


class Order(BaseModel):
    unit_uuid: UUID
    legacy_id: int
    number: str
    price: int
