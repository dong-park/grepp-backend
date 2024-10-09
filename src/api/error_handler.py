from fastapi import Request, FastAPI, HTTPException
from starlette.responses import JSONResponse


class CustomException(Exception):
    def __init__(self, name: str, code: str, message: str):
        self.name = name
        self.code = code
        self.message = message


def exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
        }
    )
