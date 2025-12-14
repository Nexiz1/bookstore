"""FastAPI dependency injection module.

This module provides dependency injection functions for authentication,
authorization, and service layer instantiation.
"""

from typing import Generator, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.exceptions.auth_exceptions import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.book_service import BookService
from app.services.cart_service import CartService
from app.services.favorite_service import FavoriteService
from app.services.order_service import OrderService
from app.services.ranking_service import RankingService
from app.services.review_service import ReviewService
from app.services.sale_service import SaleService
from app.services.seller_service import SellerService
from app.services.settlement_service import SettlementService
from app.services.user_service import UserService


def get_db() -> Generator[Session, None, None]:
    """Provide database session for request lifecycle.

    Yields:
        Session: SQLAlchemy database session.

    Note:
        Session is automatically closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ Auth Dependencies ============
def get_current_user(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> User:
    """Extract and validate current user from JWT token.

    Args:
        authorization: Bearer token from Authorization header.
        db: Database session dependency.

    Returns:
        User: Authenticated user object.

    Raises:
        UnauthorizedException: If token is invalid or user not found.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException()

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))

    if not user:
        raise UnauthorizedException("User not found")

    # 계정 비활성화 여부 확인
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract current user from JWT token without raising exceptions.

    Args:
        authorization: Bearer token from Authorization header.
        db: Database session dependency.

    Returns:
        Optional[User]: User object if valid token, None otherwise.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.split(" ")[1]
        payload = decode_token(token)

        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository(db)
        return user_repo.get_by_id(int(user_id))
    except Exception:
        # Silently handle any token parsing or database errors
        return None


def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(f"Required role: {', '.join(allowed_roles)}")
        return current_user

    return role_checker


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify current user has admin role.

    This is a convenience dependency for endpoints requiring admin access.
    Alternative to using Depends(require_role("admin")).

    Args:
        current_user: Authenticated user from get_current_user dependency.

    Returns:
        User: The admin user object.

    Raises:
        ForbiddenException: If user is not an admin.
    """
    if current_user.role != "admin":
        raise ForbiddenException("Admin access required")
    return current_user


def get_seller_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify current user has seller or admin role.

    This is a convenience dependency for endpoints requiring seller access.
    Admins are also granted seller privileges.

    Args:
        current_user: Authenticated user from get_current_user dependency.

    Returns:
        User: The seller or admin user object.

    Raises:
        ForbiddenException: If user is neither seller nor admin.
    """
    if current_user.role not in ["seller", "admin"]:
        raise ForbiddenException("Seller access required")
    return current_user


# ============ Service Dependencies ============
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_seller_service(db: Session = Depends(get_db)) -> SellerService:
    return SellerService(db)


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)


def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    return CartService(db)


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(db)


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    return FavoriteService(db)


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    return RankingService(db)


def get_sale_service(db: Session = Depends(get_db)) -> SaleService:
    return SaleService(db)


def get_settlement_service(db: Session = Depends(get_db)) -> SettlementService:
    return SettlementService(db)
