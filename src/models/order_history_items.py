from datetime import datetime

from pydantic import BaseModel

__all__ = ('OrderHistoryItem',)


class OrderHistoryItem(BaseModel):
    title: str
    user_name: str | None
    created_at: datetime
