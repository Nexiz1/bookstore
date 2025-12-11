class OrderException(Exception):
    def __init__(self, message: str = "Order error"):
        self.message = message
        super().__init__(self.message)


class OrderNotFoundException(OrderException):
    def __init__(self, message: str = "Order not found"):
        super().__init__(message)


class OrderCancelNotAllowedException(OrderException):
    def __init__(self, message: str = "This order cannot be cancelled"):
        super().__init__(message)


class OrderItemNotFoundException(OrderException):
    def __init__(self, message: str = "Order item not found"):
        super().__init__(message)
