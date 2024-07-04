from uuid import UUID

from pydantic import BaseModel

__all__ = ('Unit',)


class Unit(BaseModel):
    name: str
    uuid: UUID
    account_name: str
