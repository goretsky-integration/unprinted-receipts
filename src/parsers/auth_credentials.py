import httpx
from pydantic import ValidationError

from exceptions import AuthCredentialsParseError
from logger import create_logger
from models import AccountCookies

__all__ = ('parse_account_cookies_response',)

logger = create_logger('parser')


def parse_account_cookies_response(
        response: httpx.Response,
        account_name: str,
) -> AccountCookies:
    try:
        return AccountCookies.model_validate_json(response.text)
    except ValidationError as error:
        logger.error(
            'Account cookies response does not match the expected schema',
            extra={'account_name': account_name},
        )
        raise AuthCredentialsParseError(account_name=account_name) from error
    except ValueError:
        logger.error(
            'Account cookies response is not a JSON',
            extra={'account_name': account_name},
        )
        raise AuthCredentialsParseError(account_name=account_name)
