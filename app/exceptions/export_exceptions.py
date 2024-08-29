from fastapi import status
from gspread.exceptions import GSpreadException
from app.core.error_handler import HTTPCustomException



class NotFound(HTTPCustomException):
    DEFAULT_MESSAGE = "Export Not Found"

    def __init__(self, message: str = DEFAULT_MESSAGE, **kwargs):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, msg=message, **kwargs)

class CellLimitException(GSpreadException):
    DEFAULT_MESSAGE = "Google spreadsheet cell limit reached"
    def __init__(self, message: str = DEFAULT_MESSAGE, **kwargs):
        # Call the base class constructor with the parameters it needs
        super().__init__(msg=message, **kwargs)

