"""Security utilities module.

This module provides password hashing and JWT token management functions
using modern security best practices (Argon2id for passwords).
"""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"

# pwdlib 권장 설정 사용 (Argon2id가 기본)
pwd_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.

    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2id algorithm.

    Args:
        password: Plain text password to hash.

    Returns:
        str: Hashed password string.
    """
    return pwd_hash.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Payload data to encode in token.
        expires_delta: Optional custom expiration time.

    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token.

    Args:
        data: Payload data to encode in token.
        expires_delta: Optional custom expiration time.

    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token.

    Args:
        token: JWT token string to decode.

    Returns:
        Optional[dict]: Decoded payload if valid, None if expired or invalid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
