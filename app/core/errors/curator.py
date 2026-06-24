class CuratorNotFoundError(Exception):
    def __init__(self, curator_id: str) -> None:
        self.curator_id = curator_id
        self.message = f"Curator {curator_id} not found"
        super().__init__(self.message)


class CuratorValidationError(Exception):
    def __init__(self, message: str = "Ошибка валидации данных куратора") -> None:
        self.message = message
        super().__init__(self.message)


class CuratorAssignmentError(Exception):
    def __init__(self, message: str = "Ошибка назначения куратора") -> None:
        self.message = message
        super().__init__(self.message)


class CuratorAlreadyAssignedError(CuratorAssignmentError):
    def __init__(self, message: str = "Обращение уже назначено этому куратору") -> None:
        super().__init__(message)
