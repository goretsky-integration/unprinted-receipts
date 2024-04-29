from pydantic import BaseModel

__all__ = ('AccountCookies',)


class AccountCookies(BaseModel):
    account_name: str
    cookies: dict[str, str]
