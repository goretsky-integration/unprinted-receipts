import asyncio
from dataclasses import dataclass

from connections.auth_credentials_storage import (
    AuthCredentialsStorageConnection,
)
from exceptions import ApplicationError, UnexpectedError
from logger import create_logger
from models import AccountCookies
from parsers import parse_account_cookies_response

__all__ = (
    'AccountCookiesFetcher',
    'AccountCookiesFetchResult',
    'AccountCookiesFetchAllResult',
)

from tasks_executor import execute_batched_tasks

logger = create_logger('auth_credentials_fetcher')


@dataclass(frozen=True, slots=True)
class AccountCookiesFetchResult:
    account_name: str
    result: AccountCookies | None = None
    error: ApplicationError | None = None


@dataclass(frozen=True, slots=True)
class AccountCookiesFetchAllResult:
    results: list[AccountCookies]
    errors: list[ApplicationError]


class AccountCookiesFetcher:

    def __init__(self, connection: AuthCredentialsStorageConnection):
        self.__connection = connection
        self.__account_names_registry: set[str] = set()

    def register_account_name(self, account_name: str) -> None:
        self.__account_names_registry.add(account_name)

    async def fetch_account_name(self, account_name: str) -> AccountCookies:
        response = await self.__connection.get_account_cookies(
            account_name=account_name,
        )
        return parse_account_cookies_response(
            response=response,
            account_name=account_name,
        )

    async def try_fetch_account_name(
            self,
            account_name: str,
    ) -> AccountCookiesFetchResult:
        try:
            account_cookies = await self.fetch_account_name(account_name)
        except ApplicationError as error:
            return AccountCookiesFetchResult(
                error=error,
                account_name=account_name,
            )
        except Exception as error:
            return AccountCookiesFetchResult(
                error=UnexpectedError(exception=error),
                account_name=account_name,
            )
        return AccountCookiesFetchResult(
            result=account_cookies,
            account_name=account_name,
        )

    async def fetch_all(self) -> AccountCookiesFetchAllResult:
        coroutines = [
            self.try_fetch_account_name(account_name)
            for account_name in self.__account_names_registry
        ]

        results: list[AccountCookies] = []
        errors: list[ApplicationError] = []

        async for tasks in execute_batched_tasks(coroutines, batch_size=5):
            for task in tasks:
                exception = task.exception()
                if exception is not None:
                    logger.exception(
                        'Failed to fetch account cookies',
                        exc_info=exception,
                    )
                    continue
                result = task.result()
                if result.error is not None:
                    errors.append(result.error)
                else:
                    results.append(result.result)

        return AccountCookiesFetchAllResult(results=results, errors=errors)
