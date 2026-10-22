from pathlib import Path
from time import sleep
from uuid import uuid4

from PIL import Image

from src.tasks.tasks_app import celery_instance

IMAGES_DIR = Path("src/static/images")
IMAGE_WIDTHS = (10000, 500, 200)


@celery_instance.task
def test_task():
    print("start")
    sleep(5)
    return "end"


@celery_instance.task
def resize_image(image_path: str):

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    image_id = uuid4().hex

    image = Image.open(image_path)

    # Чтобы JPEG нормально сохранялся, например если пришёл PNG с alpha
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    result = {}

    for width in IMAGE_WIDTHS:
        # Не увеличиваем картинку, если оригинал меньше нужного размера
        target_width = min(width, image.width)

        ratio = target_width / image.width
        target_height = int(image.height * ratio)

        resized_image = image.resize(
            (target_width, target_height),
            Image.Resampling.LANCZOS,
        )

        filename = f"{image_id}_{width}.webp"
        filepath = IMAGES_DIR / filename

        resized_image.save(
            filepath,
            format="WEBP",
            quality=85,
            method=6,
        )

        result[width] = str(filepath)

    return result


# async def send_emails_to_users_with_today_checkin_helper():
#     print('я запускаюсь')
#     async with DBManager(session_factory=null_pull_session_maker) as db:
#         bookings = await db.bookings.get_bookings_with_today_checkin()
#         print(bookings)
#
#
# @celery_instance.task(name='booking_today_checkin')
# def send_emails_to_users_with_today_checkin():
#     asyncio.run(send_emails_to_users_with_today_checkin_helper())
