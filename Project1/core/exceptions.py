from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


def request_exception_handler(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exec: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exec.errors()}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exec: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"}
        )
