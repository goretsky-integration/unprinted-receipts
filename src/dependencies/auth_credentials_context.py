from fast_depends import Depends

from auth_credentials_context import AuthCredentialsContext
from connections import AuthCredentialsStorageConnection
from dependencies.connections import get_auth_credentials_storage_connection

__all__ = ('get_auth_credentials_context',)


async def get_auth_credentials_context(
        auth_credentials_storage_connection: (
                AuthCredentialsStorageConnection
        ) = Depends(
            get_auth_credentials_storage_connection,
        ),
) -> AuthCredentialsContext:
    return AuthCredentialsContext(auth_credentials_storage_connection)
