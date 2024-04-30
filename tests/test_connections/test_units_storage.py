import httpx
import pytest
import pytest_asyncio

from connections.units_storage import UnitsStorageConnection
from new_types import UnitsStorageHttpClient


@pytest_asyncio.fixture(scope="session")
async def connection() -> UnitsStorageConnection:
    async with httpx.AsyncClient(base_url='https://test_url') as http_client:
        http_client = UnitsStorageHttpClient(http_client)
        yield UnitsStorageConnection(http_client)


@pytest.mark.asyncio
async def test_units_storage_connection(httpx_mock, connection):
    expected_data = {
        "units": [{"id": 1, "name": "unit1"}, {"id": 2, "name": "unit2"}]
    }

    httpx_mock.add_response(
        status_code=200,
        json=expected_data,
    )

    response = await connection.get_units()

    assert response.status_code == 200
    assert response.json() == expected_data
