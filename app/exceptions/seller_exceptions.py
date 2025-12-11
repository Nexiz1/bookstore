class SellerException(Exception):
    def __init__(self, message: str = "Seller error"):
        self.message = message
        super().__init__(self.message)


class SellerNotFoundException(SellerException):
    def __init__(self, message: str = "Seller profile not found"):
        super().__init__(message)


class SellerAlreadyExistsException(SellerException):
    def __init__(self, message: str = "Seller profile already exists"):
        super().__init__(message)


class NotSellerException(SellerException):
    def __init__(self, message: str = "User is not a seller"):
        super().__init__(message)
