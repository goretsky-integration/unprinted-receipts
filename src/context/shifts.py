from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar
from uuid import UUID

from connections.dodo_is import DodoIsConnection
from exceptions import ApplicationError, UnexpectedError
from models import Shift, Order
from parsers.shift_management import parse_shifts_response, parse_shift_response
from tasks_executor import execute_batched_tasks

__all__ = ('ShiftsFetcher',)

T = TypeVar('T')


@dataclass(frozen=True, slots=True, kw_only=True)
class FetchResult(Generic[T]):
    unit_uuid: UUID
    result: list[T] | None = None
    exception: ApplicationError | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class FetchAllResult(Generic[T]):
    results: list[T]
    errors: list[ApplicationError]


class ShiftsFetcher:

    def __init__(self, dodo_is_connection: DodoIsConnection):
        self.__connection = dodo_is_connection
        self.__unit_uuids_and_cookies_registry = []

    def register_units(
            self,
            unit_uuids: Iterable[UUID],
            cookies: dict[str, str],
    ) -> None:
        for unit_uuid in unit_uuids:
            self.__unit_uuids_and_cookies_registry.append((unit_uuid, cookies))

    async def fetch_unit(
            self,
            unit_uuid: UUID,
            cookies: dict[str, str],
    ) -> list[Shift]:
        response = await self.__connection.get_shifts(cookies=cookies)
        return parse_shifts_response(response=response, unit_uuid=unit_uuid)

    async def try_fetch_unit(
            self,
            unit_uuid: UUID,
            cookies: dict[str, str],
    ) -> FetchResult[list[Shift]]:
        try:
            shifts = await self.fetch_unit(unit_uuid=unit_uuid, cookies=cookies)
        except ApplicationError as error:
            return FetchResult(unit_uuid=unit_uuid, exception=error)
        except Exception as error:
            return FetchResult(
                unit_uuid=unit_uuid,
                exception=UnexpectedError(exception=error),
            )
        return FetchResult(unit_uuid=unit_uuid, result=shifts)

    async def fetch_all(self) -> FetchAllResult[Shift]:
        coroutines = [
            self.try_fetch_unit(
                unit_uuid=unit_uuid,
                cookies=cookies,
            )
            for unit_uuid, cookies in
            self.__unit_uuids_and_cookies_registry
        ]

        results: list[Shift] = []
        errors: list[ApplicationError] = []

        async for tasks in execute_batched_tasks(coroutines=coroutines):

            for task in tasks:
                result = task.result()
                if result.exception is not None:
                    errors.append(result.exception)
                else:
                    results += result.result

        return FetchAllResult(results=results, errors=errors)


class ShiftDetailFetcher:

    def __init__(self, dodo_is_connection: DodoIsConnection):
        self.__connection = dodo_is_connection
        self.__shifts_and_cookies_registry = []

    def register_shift(
            self,
            shift: Shift,
            cookies: dict[str, str],
    ) -> None:
        self.__shifts_and_cookies_registry.append((shift, cookies))

    async def fetch_shift(
            self,
            shift: Shift,
            cookies: dict[str, str],
    ) -> list[Order]:
        response = await self.__connection.get_shift(
            shift_legacy_id=shift.legacy_id,
            cookies=cookies,
        )
        return parse_shift_response(
            response=response,
            unit_uuid=shift.unit_uuid,
        )

    async def try_fetch_shift(
            self,
            shift: Shift,
            cookies: dict[str, str],
    ) -> FetchResult[list[Order]]:
        try:
            orders = await self.fetch_shift(shift=shift, cookies=cookies)
        except ApplicationError as error:
            return FetchResult(unit_uuid=shift.unit_uuid, exception=error)
        except Exception as error:
            return FetchResult(
                unit_uuid=shift.unit_uuid,
                exception=UnexpectedError(exception=error),
            )
        return FetchResult(unit_uuid=shift.unit_uuid, result=orders)

    async def fetch_all(self) -> FetchAllResult[Order]:
        coroutines = [
            self.try_fetch_shift(shift=shift, cookies=cookies)
            for shift, cookies in
            self.__shifts_and_cookies_registry
        ]

        results: list[Order] = []
        errors: list[ApplicationError] = []

        async for tasks in execute_batched_tasks(coroutines=coroutines):

            for task in tasks:
                result = task.result()
                if result.exception is not None:
                    errors.append(result.exception)
                else:
                    results += result.result

        return FetchAllResult(results=results, errors=errors)
