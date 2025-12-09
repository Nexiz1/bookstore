class InternalServerException(Exception):
    def __init__(self, message: str = "Internal server error"):
        self.message = message
        super().__init__(self.message)

class ServiceUnavailableException(Exception):
    def __init__(self, message: str = "Service temporarily unavailable"):
        self.message = message
        super().__init__(self.message)
