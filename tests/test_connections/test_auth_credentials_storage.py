import httpx
import pytest
import pytest_asyncio

from connections import AuthCredentialsStorageConnection
from new_types import AuthCredentialsStorageHttpClient


@pytest_asyncio.fixture(scope="session")
async def connection() -> AuthCredentialsStorageConnection:
    async with httpx.AsyncClient(base_url='https://test_url') as http_client:
        http_client = AuthCredentialsStorageHttpClient(http_client)
        yield AuthCredentialsStorageConnection(http_client)


@pytest.mark.asyncio
async def test_auth_credentials_storage_connection_get_accounts(
        httpx_mock,
        connection,
):
    expected_data = [
        {'account_name': 'account1'},
        {'account_name': 'account2'},
        {'account_name': 'account3'},
    ]

    httpx_mock.add_response(
        status_code=200,
        json=expected_data,
    )

    response = await connection.get_accounts()

    assert response.status_code == 200
    assert response.json() == expected_data


@pytest.mark.asyncio
async def test_auth_credentials_storage_connection_get_account_cookies(
        httpx_mock,
        connection,
):
    account_name = 'account1'
    expected_data = {
        'account_name': account_name,
        'cookies': {
            'cookie1': 'value1',
            'cookie2': 'value2',
        },
    }

    httpx_mock.add_response(
        status_code=200,
        json=expected_data,
    )

    response = await connection.get_account_cookies(account_name=account_name)

    assert response.status_code == 200
    assert response.json() == expected_data
