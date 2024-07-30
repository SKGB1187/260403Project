class DBActionResult[T]:
    def __init__(self, value: T, is_success: bool, message: str) -> None:
        self.value = value
        self.is_success = is_success
        self.message = message
