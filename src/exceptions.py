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
