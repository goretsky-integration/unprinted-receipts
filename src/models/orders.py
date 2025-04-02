from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = ('Order',)


class Order(BaseModel):
    unit_uuid: UUID
    id: Annotated[UUID, Field(validation_alias='Id')]
    number: Annotated[str, Field(validation_alias='Number')]
    price: Annotated[int, Field(validation_alias='Sum')]
