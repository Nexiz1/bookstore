from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.item_exceptions import ItemNotFoundException
from app.exceptions.user_exceptions import UserNotFoundException, UserAlreadyExistsException
from app.exceptions.server_exceptions import InternalServerException, ServiceUnavailableException

async def item_not_found_exception_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": exc.message, "data": None},
    )

    
async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": exc.message, "data": None},
    )

async def user_already_exists_exception_handler(request: Request, exc: UserAlreadyExistsException):
    return JSONResponse(
        status_code=409,
        content={"status": "error", "message": exc.message, "data": None},
    )

async def internal_server_exception_handler(request: Request, exc: InternalServerException):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": exc.message, "data": None},
    )

async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailableException):
    return JSONResponse(
        status_code=503,
        content={"status": "error", "message": exc.message, "data": None},
    )


def add_exception_handlers(app):
    """Exception handler들을 일괄 추가하는 함수"""
    app.add_exception_handler(ItemNotFoundException, item_not_found_exception_handler)
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_exception_handler)
    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)
    app.add_exception_handler(InternalServerException, internal_server_exception_handler)
    app.add_exception_handler(ServiceUnavailableException, service_unavailable_exception_handler)
