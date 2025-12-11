from fastapi import Request
from fastapi.responses import JSONResponse

# Auth exceptions
from app.exceptions.auth_exceptions import (
    ForbiddenException,
    InvalidCredentialsException,
    InvalidTokenException,
    UnauthorizedException,
)

# Book exceptions
from app.exceptions.book_exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    BookNotOwnedException,
)

# Cart exceptions
from app.exceptions.cart_exceptions import (
    CartEmptyException,
    CartItemAlreadyExistsException,
    CartItemNotFoundException,
)

# Favorite exceptions
from app.exceptions.favorite_exceptions import (
    FavoriteAlreadyExistsException,
    FavoriteNotFoundException,
)

# Order exceptions
from app.exceptions.order_exceptions import (
    OrderCancelNotAllowedException,
    OrderItemNotFoundException,
    OrderNotFoundException,
)

# Review exceptions
from app.exceptions.review_exceptions import (
    ReviewAlreadyExistsException,
    ReviewNotAllowedException,
    ReviewNotFoundException,
    ReviewNotOwnedException,
)

# Sale exceptions
from app.exceptions.sale_exceptions import (
    SaleBookAlreadyExistsException,
    SaleNotFoundException,
    SaleNotOwnedException,
)

# Seller exceptions
from app.exceptions.seller_exceptions import (
    NotSellerException,
    SellerAlreadyExistsException,
    SellerNotFoundException,
)

# Server exceptions
from app.exceptions.server_exceptions import (
    InternalServerException,
    ServiceUnavailableException,
)

# User exceptions
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)


def create_error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message, "data": None},
    )


# 401 Unauthorized handlers
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    return create_error_response(401, exc.message)

async def invalid_token_handler(request: Request, exc: InvalidTokenException):
    return create_error_response(401, exc.message)

async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return create_error_response(401, exc.message)


# 403 Forbidden handlers
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return create_error_response(403, exc.message)

async def not_seller_handler(request: Request, exc: NotSellerException):
    return create_error_response(403, exc.message)

async def book_not_owned_handler(request: Request, exc: BookNotOwnedException):
    return create_error_response(403, exc.message)

async def review_not_owned_handler(request: Request, exc: ReviewNotOwnedException):
    return create_error_response(403, exc.message)

async def sale_not_owned_handler(request: Request, exc: SaleNotOwnedException):
    return create_error_response(403, exc.message)

async def review_not_allowed_handler(request: Request, exc: ReviewNotAllowedException):
    return create_error_response(403, exc.message)


# 404 Not Found handlers
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return create_error_response(404, exc.message)

async def book_not_found_handler(request: Request, exc: BookNotFoundException):
    return create_error_response(404, exc.message)

async def seller_not_found_handler(request: Request, exc: SellerNotFoundException):
    return create_error_response(404, exc.message)

async def cart_item_not_found_handler(request: Request, exc: CartItemNotFoundException):
    return create_error_response(404, exc.message)

async def order_not_found_handler(request: Request, exc: OrderNotFoundException):
    return create_error_response(404, exc.message)

async def order_item_not_found_handler(request: Request, exc: OrderItemNotFoundException):
    return create_error_response(404, exc.message)

async def review_not_found_handler(request: Request, exc: ReviewNotFoundException):
    return create_error_response(404, exc.message)

async def favorite_not_found_handler(request: Request, exc: FavoriteNotFoundException):
    return create_error_response(404, exc.message)

async def sale_not_found_handler(request: Request, exc: SaleNotFoundException):
    return create_error_response(404, exc.message)


# 409 Conflict handlers
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    return create_error_response(409, exc.message)

async def book_already_exists_handler(request: Request, exc: BookAlreadyExistsException):
    return create_error_response(409, exc.message)

async def seller_already_exists_handler(request: Request, exc: SellerAlreadyExistsException):
    return create_error_response(409, exc.message)

async def cart_item_already_exists_handler(request: Request, exc: CartItemAlreadyExistsException):
    return create_error_response(409, exc.message)

async def review_already_exists_handler(request: Request, exc: ReviewAlreadyExistsException):
    return create_error_response(409, exc.message)

async def favorite_already_exists_handler(request: Request, exc: FavoriteAlreadyExistsException):
    return create_error_response(409, exc.message)

async def sale_book_already_exists_handler(request: Request, exc: SaleBookAlreadyExistsException):
    return create_error_response(409, exc.message)


# 400 Bad Request handlers
async def cart_empty_handler(request: Request, exc: CartEmptyException):
    return create_error_response(400, exc.message)

async def order_cancel_not_allowed_handler(request: Request, exc: OrderCancelNotAllowedException):
    return create_error_response(400, exc.message)


# 500 Server Error handlers
async def internal_server_handler(request: Request, exc: InternalServerException):
    return create_error_response(500, exc.message)

async def service_unavailable_handler(request: Request, exc: ServiceUnavailableException):
    return create_error_response(503, exc.message)


def add_exception_handlers(app):
    """Exception handler들을 일괄 추가하는 함수"""
    # 401 Unauthorized
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)
    app.add_exception_handler(InvalidTokenException, invalid_token_handler)
    app.add_exception_handler(UnauthorizedException, unauthorized_handler)

    # 403 Forbidden
    app.add_exception_handler(ForbiddenException, forbidden_handler)
    app.add_exception_handler(NotSellerException, not_seller_handler)
    app.add_exception_handler(BookNotOwnedException, book_not_owned_handler)
    app.add_exception_handler(ReviewNotOwnedException, review_not_owned_handler)
    app.add_exception_handler(SaleNotOwnedException, sale_not_owned_handler)
    app.add_exception_handler(ReviewNotAllowedException, review_not_allowed_handler)

    # 404 Not Found
    app.add_exception_handler(UserNotFoundException, user_not_found_handler)
    app.add_exception_handler(BookNotFoundException, book_not_found_handler)
    app.add_exception_handler(SellerNotFoundException, seller_not_found_handler)
    app.add_exception_handler(CartItemNotFoundException, cart_item_not_found_handler)
    app.add_exception_handler(OrderNotFoundException, order_not_found_handler)
    app.add_exception_handler(OrderItemNotFoundException, order_item_not_found_handler)
    app.add_exception_handler(ReviewNotFoundException, review_not_found_handler)
    app.add_exception_handler(FavoriteNotFoundException, favorite_not_found_handler)
    app.add_exception_handler(SaleNotFoundException, sale_not_found_handler)

    # 409 Conflict
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)
    app.add_exception_handler(BookAlreadyExistsException, book_already_exists_handler)
    app.add_exception_handler(SellerAlreadyExistsException, seller_already_exists_handler)
    app.add_exception_handler(CartItemAlreadyExistsException, cart_item_already_exists_handler)
    app.add_exception_handler(ReviewAlreadyExistsException, review_already_exists_handler)
    app.add_exception_handler(FavoriteAlreadyExistsException, favorite_already_exists_handler)
    app.add_exception_handler(SaleBookAlreadyExistsException, sale_book_already_exists_handler)

    # 400 Bad Request
    app.add_exception_handler(CartEmptyException, cart_empty_handler)
    app.add_exception_handler(OrderCancelNotAllowedException, order_cancel_not_allowed_handler)

    # 500 Server Error
    app.add_exception_handler(InternalServerException, internal_server_handler)
    app.add_exception_handler(ServiceUnavailableException, service_unavailable_handler)
