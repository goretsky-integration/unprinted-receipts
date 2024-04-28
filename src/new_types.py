from typing import NewType

import httpx

__all__ = (
    'AuthCredentialsStorageHttpClient',
    'UnitsStorageHttpClient',
    'DodoIsHttpClient',
)

AuthCredentialsStorageHttpClient = NewType(
    'AuthCredentialsStorageHttpClient',
    httpx.AsyncClient,
)

UnitsStorageHttpClient = NewType('UnitsStorageHttpClient', httpx.AsyncClient)

DodoIsHttpClient = NewType('DodoIsHttpClient', httpx.AsyncClient)
