import logging

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import httpx
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.ai_exception import get_ai_message
from app.exceptions.custom import AppException
from app.exceptions.database import get_database_message
from app.exceptions.error_codes import ErrorCode
from app.exceptions.responses import error_response
from app.exceptions.ai_exception import AIException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                exc.message,
                exc.error_code,
                exc.status_code,
                exc.details,
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                exc.detail,
                "HTTP_ERROR",
                exc.status_code,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=422,
            content=error_response(
                "Validation Error",
                ErrorCode.VALIDATION_ERROR,
                422,
                # errors() can carry a raw exception object under "ctx", which
                # json.dumps cannot serialise — that turned a 422 into a 500
                jsonable_encoder(exc.errors()),
            ),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
    ):
        # the client only ever sees a generic message, so the real statement/constraint has to
        # reach the log or the failure is undiagnosable
        logger.exception("Database error on %s %s", request.method, request.url.path)

        message, code, status = get_database_message(exc)

        return JSONResponse(
            status_code=status,
            content=error_response(
                message,
                code,
                status,
            ),
        )

    @app.exception_handler(AIException)
    async def ai_exception_handler(
        request: Request,
        exc: AIException,
    ):
        # AIException subclasses AppException, so this more specific handler is the one that
        # runs — it has to forward details itself or the AI service's own error body, which
        # handle_ai_exception went to the trouble of capturing, is dropped here.
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                exc.message,
                exc.error_code,
                exc.status_code,
                exc.details,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)

        return JSONResponse(
            status_code=500,
            content=error_response(
                "Internal Server Error",
                ErrorCode.INTERNAL_SERVER_ERROR,
                500,
            ),
        )
