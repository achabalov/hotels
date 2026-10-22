import shutil

from fastapi import APIRouter, BackgroundTasks, UploadFile

from src.tasks.tasks import resize_image

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("")
def upload_image(file: UploadFile, background_task: BackgroundTasks):
    image_path = f"src/static/images/{file.filename}"
    with open(image_path, "wb+") as f:
        shutil.copyfileobj(file.file, f)

    background_task.add_task(resize_image, image_path)
