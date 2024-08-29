from fastapi import status, Request, HTTPException
from fastapi.responses import JSONResponse


class HTTPCustomException(HTTPException):
    def __init__(self, status_code: int, msg: str, loc: list = [], type_value: str = None):
        super().__init__(status_code=status_code, detail=self.create_detail(msg, loc, type_value))

    @staticmethod
    def create_detail(msg: str, loc: list = [], type_value: str = None):
        return {'detail': [{'loc': loc, 'msg': msg, 'type': type_value}]}


def exception_handler(request: Request, e: HTTPCustomException):
    return JSONResponse(status_code=e.status_code, content=e.detail)


def fatal_exception_handler(request: Request, e: Exception):
    detail = HTTPCustomException.create_detail("Internal Error Server")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=detail)
