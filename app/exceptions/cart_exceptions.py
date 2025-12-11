class CartException(Exception):
    def __init__(self, message: str = "Cart error"):
        self.message = message
        super().__init__(self.message)


class CartItemNotFoundException(CartException):
    def __init__(self, message: str = "Cart item not found"):
        super().__init__(message)


class CartItemAlreadyExistsException(CartException):
    def __init__(self, message: str = "This book is already in your cart"):
        super().__init__(message)


class CartEmptyException(CartException):
    def __init__(self, message: str = "Cart is empty"):
        super().__init__(message)
