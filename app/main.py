from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.router import api_router
from app.schemas.api_response import APIResponse

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": getattr(exc, "message", "An error occurred"),
            "error": str(exc.detail),
            "status": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Error",
            "error": str(exc.errors()),
            "status": 422
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "error": str(exc),
            "status": 500
        }
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"], response_model=APIResponse[dict])
def health():
    return APIResponse(
        success=True,
        message="Service is healthy",
        data={"status": "ok", "project": settings.PROJECT_NAME},
        status=200
    )
