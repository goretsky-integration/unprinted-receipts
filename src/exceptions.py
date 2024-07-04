__all__ = (
    'ApplicationError',
    'AccountCookiesDoNotExistError',
    'AuthCredentialsParseError',
    'HttpError',
    'UnexpectedError',
    'UnprintedReceiptsPageParseError',
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


class AuthCredentialsParseError(ApplicationError):
    """Raised when auth credentials could not be parsed."""
    code: str = 'AUTH_CREDENTIALS_PARSE_ERROR'
    message: str = 'Auth credentials parse error'

    def __init__(self, account_name: str):
        super().__init__()
        self.account_name = account_name


class HttpError(ApplicationError):
    """Raised when HTTP request failed."""
    code: str = 'HTTP_ERROR'
    message: str = 'HTTP request failed'

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs


class UnexpectedError(ApplicationError):
    """Raised when unexpected error occurred."""
    code: str = 'UNEXPECTED_ERROR'
    message: str = 'Unexpected error occurred'

    def __init__(self, exception: Exception):
        super().__init__()
        self.exception = exception


class UnprintedReceiptsPageParseError(ApplicationError):
    """Raised when unprinted receipts page could not be parsed."""
    code: str = 'UNPRINTED_RECEIPTS_PAGE_PARSE_ERROR'
    message: str = 'Unprinted receipts page parse error'

    def __init__(self, unit_name: str, response_body: str):
        super().__init__()
        self.unit_name = unit_name
        self.response_body = response_body
