class ReviewException(Exception):
    def __init__(self, message: str = "Review error"):
        self.message = message
        super().__init__(self.message)


class ReviewNotFoundException(ReviewException):
    def __init__(self, message: str = "Review not found"):
        super().__init__(message)


class ReviewAlreadyExistsException(ReviewException):
    def __init__(self, message: str = "You have already reviewed this item"):
        super().__init__(message)


class ReviewNotAllowedException(ReviewException):
    def __init__(self, message: str = "You can only review items you have purchased"):
        super().__init__(message)


class ReviewNotOwnedException(ReviewException):
    def __init__(self, message: str = "You don't own this review"):
        super().__init__(message)
