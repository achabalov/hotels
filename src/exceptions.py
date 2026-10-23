class AppError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class InvalidDataError(AppError):
    status_code = 422


def validate_dates(date_from, date_to):
    if date_to <= date_from:
        raise InvalidDataError("Дата выезда должна быть позже даты заезда")
