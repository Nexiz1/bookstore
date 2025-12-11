class AuthException(Exception):
    def __init__(self, message: str = "Authentication error"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsException(AuthException):
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class InvalidTokenException(AuthException):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class UnauthorizedException(AuthException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message)


class ForbiddenException(AuthException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)
