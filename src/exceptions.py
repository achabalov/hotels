class AppError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass


class InvalidDataError(AppError):
    pass


class AuthenticationError(AppError):
    pass


class TokenExpiredError(AuthenticationError):
    pass


class InvalidTokenError(AuthenticationError):
    pass


class InvalidImageError(InvalidDataError):
    pass


class ImageTooLargeError(AppError):
    pass


class UnsupportedImageFormatError(AppError):
    pass


class ImageStorageError(AppError):
    pass


def validate_dates(date_from, date_to):
    if date_to <= date_from:
        raise InvalidDataError("Дата выезда должна быть позже даты заезда")
