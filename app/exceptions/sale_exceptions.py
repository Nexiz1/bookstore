class SaleException(Exception):
    def __init__(self, message: str = "Sale error"):
        self.message = message
        super().__init__(self.message)


class SaleNotFoundException(SaleException):
    def __init__(self, message: str = "Sale not found"):
        super().__init__(message)


class SaleBookAlreadyExistsException(SaleException):
    def __init__(self, message: str = "This book is already in this sale"):
        super().__init__(message)


class SaleNotOwnedException(SaleException):
    def __init__(self, message: str = "You don't own this sale"):
        super().__init__(message)
