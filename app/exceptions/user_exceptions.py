class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message = f"User with ID {user_id} not found"
        super().__init__(self.message)

class UserAlreadyExistsException(Exception):
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.message = f"User with email '{user_email}' already exists"
        super().__init__(self.message)
