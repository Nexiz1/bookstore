class BookException(Exception):
    def __init__(self, message: str = "Book error"):
        self.message = message
        super().__init__(self.message)


class BookNotFoundException(BookException):
    def __init__(self, message: str = "Book not found"):
        super().__init__(message)


class BookAlreadyExistsException(BookException):
    def __init__(self, message: str = "Book with this ISBN already exists"):
        super().__init__(message)


class BookNotOwnedException(BookException):
    def __init__(self, message: str = "You don't own this book"):
        super().__init__(message)
