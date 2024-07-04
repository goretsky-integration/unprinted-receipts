import httpx

from logger import create_logger
from new_types import AuthCredentialsStorageHttpClient

__all__ = ('AuthCredentialsStorageConnection',)

logger = create_logger('auth_credentials_connection')


class AuthCredentialsStorageConnection:

    def __init__(self, http_client: AuthCredentialsStorageHttpClient):
        self.__http_client = http_client

    async def get_account_cookies(self, account_name: str) -> httpx.Response:
        url = '/auth/cookies/'
        query_params = {'account_name': account_name}

        logger.debug(
            'Requesting account cookies',
            extra={'query_params': query_params},
        )
        response = await self.__http_client.get(url, params=query_params)
        logger.info(
            'Account cookies response received',
            extra={
                'query_params': query_params,
                'status_code': response.status_code,
                'response_body': response.text,
            },
        )
        return response
