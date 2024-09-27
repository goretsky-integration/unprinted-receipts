from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = ('Shift',)


class Shift(BaseModel):
    unit_uuid: UUID
    legacy_id: Annotated[int, Field(validation_alias='LegacyId')]
    started_at: Annotated[datetime, Field(validation_alias='ShiftStartedAt')]
    ended_at: Annotated[datetime | None, Field(validation_alias='ShiftEndedAt')]
