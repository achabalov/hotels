import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from src.tasks.tasks import resize_image

router = APIRouter(prefix="/images", tags=["Изображения"])
logger = logging.getLogger(__name__)
IMAGES_DIR = Path("src/static/images")
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PIXELS = 25_000_000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def remove_failed_upload(image_path: Path):
    try:
        image_path.unlink(missing_ok=True)
    except OSError:
        logger.exception("Cannot remove failed upload: %s", image_path)


def resize_uploaded_image(image_path: str):
    # Ответ уже отправлен: ошибку фоновой обработки можно только записать в лог.
    try:
        resize_image(image_path)
    except Exception:
        logger.exception("Image processing failed: %s", image_path)


@router.post("")
def upload_image(file: UploadFile, background_task: BackgroundTasks):
    image_path = IMAGES_DIR / f"{uuid4().hex}.upload"
    try:
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        size = 0
        with image_path.open("xb") as target:
            while chunk := file.file.read(64 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(413, "Максимальный размер изображения — 10 МБ")
                target.write(chunk)
        if size == 0:
            raise HTTPException(422, "Файл пуст")
        with Image.open(image_path) as image:
            if image.format not in ALLOWED_FORMATS:
                raise HTTPException(415, "Поддерживаются изображения JPEG, PNG и WEBP")
            if image.width * image.height > MAX_PIXELS:
                raise HTTPException(413, "Слишком большое разрешение изображения")
            image.verify()
        # verify проверяет структуру, load обнаруживает ошибки декодирования пикселей.
        with Image.open(image_path) as image:
            image.load()
    except Image.DecompressionBombError as exc:
        remove_failed_upload(image_path)
        raise HTTPException(413, "Слишком большое разрешение изображения") from exc
    except (UnidentifiedImageError, SyntaxError, ValueError) as exc:
        remove_failed_upload(image_path)
        raise HTTPException(422, "Файл не является корректным изображением") from exc
    except HTTPException:
        remove_failed_upload(image_path)
        raise
    except OSError as exc:
        remove_failed_upload(image_path)
        # Pillow сообщает ошибки повреждённых файлов через OSError.
        if isinstance(exc, (PermissionError, FileNotFoundError)) or exc.errno is not None:
            logger.exception("Cannot save uploaded image")
            raise HTTPException(503, "Хранилище изображений временно недоступно") from exc
        raise HTTPException(422, "Изображение повреждено") from exc
    finally:
        file.file.close()

    background_task.add_task(resize_uploaded_image, str(image_path))
    return {"status": "accepted", "filename": image_path.name}
