class FavoriteException(Exception):
    def __init__(self, message: str = "Favorite error"):
        self.message = message
        super().__init__(self.message)


class FavoriteNotFoundException(FavoriteException):
    def __init__(self, message: str = "Favorite not found"):
        super().__init__(message)


class FavoriteAlreadyExistsException(FavoriteException):
    def __init__(self, message: str = "This book is already in your favorites"):
        super().__init__(message)
