"""
SpiderGlass AI – Centralised exception definitions and HTTP error handlers.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class SpiderGlassException(Exception):
    """Base exception for all SpiderGlass domain errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(SpiderGlassException):
    def __init__(self, resource: str, identifier):
        super().__init__(f"{resource} with id '{identifier}' not found.", 404)


class UnauthorizedException(SpiderGlassException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, 401)


class ValidationException(SpiderGlassException):
    def __init__(self, detail: str):
        super().__init__(detail, 422)


class SarvamAPIException(SpiderGlassException):
    """Raised when the Sarvam AI API returns an error."""
    def __init__(self, detail: str):
        super().__init__(f"Sarvam AI API error: {detail}", 502)


class ServiceUnavailableException(SpiderGlassException):
    def __init__(self, service: str):
        super().__init__(f"Service '{service}' is currently unavailable.", 503)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(SpiderGlassException)
    async def spiderglass_exception_handler(
        request: Request, exc: SpiderGlassException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An internal server error occurred.", "detail": str(exc)},
        )
