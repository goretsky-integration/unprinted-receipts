import asyncio
import datetime
from collections.abc import Iterable
from typing import TypeVar

import structlog.stdlib
from fast_depends import Depends, inject

import message_queue
from auth_credentials_context import AuthCredentialsContext
from config import Config, get_config
from connections import AuthCredentialsStorageConnection, UnitsStorageConnection
from dependencies import (
    get_auth_credentials_context,
    get_dodo_is_context,
    get_units_storage_connection,
)
from dodo_is_context import DodoIsContext
from filters import filter_valid_canceled_orders
from mappers import prepare_events
from parsers import parse_account_cookies_response, parse_units_response
from time_helpers import get_yesterday_this_moment

logger = structlog.stdlib.get_logger('app')

T = TypeVar('T')


def flatten(nested: Iterable[Iterable[T]]) -> list[T]:
    return [
        item
        for items in nested
        for item in items
    ]


async def process_account(
        account_name: str,
        date: datetime.date,
        auth_credentials_storage_connection: AuthCredentialsStorageConnection,
        dodo_is_context: DodoIsContext,
):
    account_cookies_response = (
        await auth_credentials_storage_connection.get_account_cookies(
            account_name=account_name,
        )
    )
    account_cookies = parse_account_cookies_response(
        response=account_cookies_response,
        account_name=account_name,
    )

    partial_orders = await dodo_is_context.get_partial_orders(
        cookies=account_cookies.cookies,
        date=date,
    )

    tasks = [
        dodo_is_context.get_detailed_order(
            cookies=account_cookies.cookies,
            partial_order=partial_order,
        )
        for partial_order in partial_orders
    ]
    detailed_orders = await asyncio.gather(*tasks, return_exceptions=False)
    return filter_valid_canceled_orders(detailed_orders)


@inject
async def main(
        units_storage_connection: UnitsStorageConnection = Depends(
            get_units_storage_connection,
        ),
        auth_credentials_context: AuthCredentialsContext = Depends(
            get_auth_credentials_context,
        ),
        dodo_is_context: DodoIsContext = Depends(get_dodo_is_context),
        yesterday: datetime.datetime = Depends(
            get_yesterday_this_moment,
            use_cache=False,
        ),
        config: Config = Depends(get_config),
):
    units_response = await units_storage_connection.get_units()
    units = parse_units_response(units_response)

    account_names = (
        await auth_credentials_context.get_shift_manager_account_names()
    )
    accounts_cookies = await auth_credentials_context.get_accounts_cookies_batch(
        account_names=account_names,
    )

    partial_orders = await dodo_is_context.get_partial_orders_batch(
        date=yesterday,
        accounts_cookies=accounts_cookies,
    )

    account_name_to_cookies = {
        account_cookies.account_name: account_cookies.cookies
        for account_cookies in accounts_cookies
    }

    detailed_orders = await dodo_is_context.get_detailed_orders_batch(
        account_name_to_cookies=account_name_to_cookies,
        partial_orders=partial_orders,
    )

    canceled_orders = filter_valid_canceled_orders(detailed_orders)

    events = prepare_events(
        unit_name_to_id={unit.name: unit.id for unit in units},
        canceled_orders=canceled_orders,
        country_code=config.dodo_is.country_code,
    )

    for event in events:
        print(event)

    await message_queue.publish_events(
        message_queue_url=config.message_queue_url,
        events=events,
    )


if __name__ == '__main__':
    asyncio.run(main())
