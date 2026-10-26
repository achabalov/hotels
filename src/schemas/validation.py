from typing import Annotated

from pydantic import BaseModel, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PatchModel(BaseModel):
    """В PATCH поля можно пропустить; null разрешён только для nullable-полей."""

    @model_validator(mode="after")
    def validate_patch(self):
        if not self.model_fields_set:
            raise ValueError("Укажите хотя бы одно поле для изменения")
        for name in self.model_fields_set - {"description"}:
            if getattr(self, name) is None:
                raise ValueError(f"Поле {name} не может быть null")
        return self
