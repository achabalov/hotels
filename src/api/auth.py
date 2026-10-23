from fastapi import APIRouter, HTTPException, Response

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.users import UserAdd, UserRequestAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", summary="Регистрация пользователя")
async def registry_user(db: DBDep, data: UserRequestAdd):
    hashed_password = AuthService().hash_password(password=data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    await db.users.add(new_user_data)
    await db.commit()

    return {"status": 200}


@router.post("/login")
async def login_user(db: DBDep, data: UserRequestAdd, response: Response):
    user = await db.users.get_user_with_hashed_password(email=data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if AuthService().verify_password(
        plain_password=data.password, hashed_password=user.hashed_password
    ):
        access_token = AuthService().create_access_token(data={"user_id": user.id})
        response.set_cookie("access_token", access_token, httponly=True)
        return {"access_token": access_token}

    raise HTTPException(status_code=401, detail="Неверный email или пароль")


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")


@router.get("/me")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await db.users.get_one_or_none(id=user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
