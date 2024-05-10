import json

import httpx
import structlog
from pydantic import ValidationError

from exceptions import AuthCredentialsParseError
from models import AccountCookies

__all__ = ('parse_accounts_response', 'parse_account_cookies_response')

logger = structlog.stdlib.get_logger('app')


def parse_accounts_response(response: httpx.Response) -> set[str]:
    response_data: dict = response.json()
    return {account['name'] for account in response_data}


def parse_account_cookies_response(
        response: httpx.Response,
        account_name: str,
) -> AccountCookies:
    try:
        response_data: dict = response.json()
        return AccountCookies.model_validate(response_data)
    except (json.JSONDecodeError, ValidationError) as error:
        logger.error('No cookies of account', account_name=account_name)
        raise AuthCredentialsParseError(account_name=account_name) from error
