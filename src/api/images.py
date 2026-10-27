from fastapi import APIRouter, BackgroundTasks, UploadFile

from src.services.images import ImagesService

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("")
async def upload_image(file: UploadFile, background_task: BackgroundTasks):
    image_path = await ImagesService().upload_image(file, background_task)
    return image_path
