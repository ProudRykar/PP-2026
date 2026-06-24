class FileValidationError(Exception):
    def __init__(self, message: str = "Ошибка валидации файла") -> None:
        super().__init__(message)
        self.message: str = message


class FileExtensionValidationError(FileValidationError):
    def __init__(self, message: str = "Недопустимое расширение файла") -> None:
        super().__init__(message)


class FileSizeValidationError(FileValidationError):
    def __init__(self, message: str = "Превышен максимальный размер файла") -> None:
        super().__init__(message)


class MessageValidationError(Exception):
    def __init__(self, message: str = "Ошибка валидации сообщения") -> None:
        super().__init__(message)
        self.message: str = message


class ClientValidationError(Exception):
    def __init__(self, message: str = "Ошибка валидации данных клиента") -> None:
        super().__init__(message)
        self.message: str = message


class EmailValidationError(ClientValidationError):
    def __init__(self, message: str = "Некорректный формат email") -> None:
        super().__init__(message)
