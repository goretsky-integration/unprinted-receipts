from uuid import UUID

__all__ = (
    'ApplicationError',
    'DetailedOrderParseError',
    'AccountCookiesDoNotExistError',
    'AuthCredentialsParseError',
)


class ApplicationError(Exception):
    """Base class for application exceptions."""
    code: str = 'APPLICATION_ERROR'
    message: str = 'Application error'

    def __init__(self):
        super().__init__(self.message)


class AccountCookiesDoNotExistError(ApplicationError):
    """Raised when account cookies not found."""
    code: str = 'ACCOUNT_COOKIES_NOT_FOUND'
    message: str = 'Account cookies not found'

    def __init__(self, account_name: str):
        super().__init__()
        self.account_name = account_name


class DetailedOrderParseError(ApplicationError):
    """Raised when detailed order page parsing failed."""
    code: str = 'DETAILED_ORDER_PARSE_ERROR'
    message: str = 'Detailed order page parsing failed'

    def __init__(self, order_id: UUID):
        super().__init__()
        self.order_id = order_id


class AuthCredentialsParseError(ApplicationError):
    """Raised when auth credentials could not be parsed."""
    code: str = 'AUTH_CREDENTIALS_PARSE_ERROR'
    message: str = 'Auth credentials parse error'

    def __init__(self, account_name: str):
        super().__init__()
        self.account_name = account_name
