import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import hash_password, generate_token, verify_password, decode_token
from models import Session, User, Adv, close_orm, init_orm


def json_response(json_data, status=200, **kwargs):
    """Для поддержки русских символов"""
    return web.json_response(
        json_data,
        status=status,
        dumps=lambda obj: json.dumps(obj, ensure_ascii=False, indent=2),
        **kwargs
    )


def get_error(msg: str | list | dict, cls):
    """Функция для обработки ошибок"""

    msg = {"error": msg}
    msg_json = json.dumps(msg)
    return cls(
        text=msg_json,
        content_type="application/json",
    )


async def add_user(session: AsyncSession, user: User):
    """Функция для создания пользователя"""

    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise get_error("User is alresdy exists", web.HTTPConflict)


async def add_adv(session: AsyncSession, adv: Adv):
    """Функция для создания объявления"""
    session.add(adv)
    try:
        await session.commit()
    except IntegrityError:
        raise get_error("Advertisement is alresdy exists", web.HTTPConflict)


async def orm_context(app: web.Application):
    """Функция для подключения к БД"""
    print("START")
    # Все что написано до yield выполнится при старте приложения
    await init_orm()
    yield
    await close_orm()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    """Middleware для запуска сессии"""

    # Будет выполняться перед каждой работой вью функции
    async with Session() as session:
        request.session = session
        response = await handler(request)

        return response


@web.middleware
async def auth_middleware(request: web.Request, handler):
    """Middleware для проверки авторизации"""

    # Не требуют авторизации
    public_routes = [("POST", "/user"), ("POST", "/login")]

    current_path = request.path
    current_method = request.method

    if (current_method, current_path) in public_routes:
        return await handler(request)

    if current_method == "GET" and (
        current_path.startswith("/advs/") or current_path.startswith("/users/")
    ):
        return await handler(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise get_error("Token is needed", web.HTTPUnauthorized)

    token = auth_header.split("Bearer ")[1]
    token_decode = decode_token(token)

    if not token_decode:
        raise get_error("Bad or expired token", web.HTTPUnauthorized)

    user = await request.session.get(User, token_decode["user_id"])
    if not user:
        raise get_error("User is not found", web.HTTPUnauthorized)

    request["user"] = user

    return await handler(request)


app = web.Application()
app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)
app.middlewares.append(auth_middleware)


class UserView(web.View):
    """Эндпоинт для работы с пользователями"""

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_user(self) -> User | None:
        user = await self.session.get(User, self.user_id)
        if user is None:
            raise get_error("User is not found", web.HTTPNotFound)
        return user

    async def get(self):
        user = await self.get_user()
        return json_response(user.dict)

    async def post(self):
        user_json = await self.request.json()
        user = User(
            name=user_json["name"], password=hash_password(user_json["password"])
        )
        await add_user(self.session, user)
        return json_response(user.id_dict)

    async def patch(self):
        user = await self.get_user()
        json_data = await self.request.json()
        if "name" in json_data:
            user.name = json_data["name"]
        if "password" in json_data:
            user.password = hash_password(json_data["password"])

        await self.session.commit()
        return json_response(user.id_dict)

    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return json_response({"status": "deleted"})


class AdvView(web.View):
    """Эндпоинт для работы с объявлениями"""

    @property
    def adv_id(self) -> int:
        return int(self.request.match_info["adv_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_adv(self) -> Adv | None:
        adv = await self.session.get(Adv, self.adv_id)
        if adv is None:
            raise get_error("Advertisement is not found", web.HTTPNotFound)
        return adv

    async def get(self):
        adv = await self.get_adv()
        return json_response(adv.dict)

    async def post(self):
        user = self.request.get("user")
        if not user:
            raise get_error("Unathorization", web.HTTPUnauthorized)

        adv_json = await self.request.json()
        adv = Adv(
            title=adv_json["title"],
            description=adv_json["description"],
            user_id=user.id,
        )
        await add_adv(self.session, adv)
        return json_response(adv.id_dict)

    async def patch(self):
        adv = await self.get_adv()
        user = self.request.get("user")

        if not user or adv.user_id != user.id:
            raise get_error("You don't have permissions", web.HTTPForbidden)

        json_data = await self.request.json()
        if "title" in json_data:
            adv.title = json_data["title"]
        if "description" in json_data:
            adv.description = json_data["description"]

        await self.session.commit()
        return json_response(adv.id_dict)

    async def delete(self):
        adv = await self.get_adv()
        user = self.request.get("user")

        if not user or adv.user_id != user.id:
            raise get_error("You don't have permissions", web.HTTPForbidden)

        await self.session.delete(adv)
        await self.session.commit()
        return json_response({"status": "deleted"})


class LoginView(web.View):
    """Эндпоинт для получения токена"""

    async def get_user_by_name(self, username: str) -> User | None:
        """Поиск пользователя по имени"""
        user = await self.request.session.scalar(
            select(User).where(User.name == username)
        )
        if not user:
            raise get_error("User is not found", web.HTTPNotFound)
        return user

    async def post(self):
        json_data = await self.request.json()
        username = json_data.get("name")
        password = json_data.get("password")

        user = await self.get_user_by_name(username)

        if not verify_password(password, user.password):
            raise get_error("Bad login or password", web.HTTPUnauthorized)

        token = generate_token(user.id)

        return json_response({"token": token, "token_type": "Bearer"})

app.add_routes(
    [
        # Пользователи
        web.get(r"/users/{user_id:\d+}", UserView),
        web.patch(r"/users/{user_id:\d+}", UserView),
        web.delete(r"/users/{user_id:\d+}", UserView),
        # Регистрация
        web.post(r"/user", UserView),
        # Авторизация
        web.post(r"/login", LoginView),
        # Объявления
        web.get(r"/advs/{adv_id:\d+}", AdvView),
        web.patch(r"/advs/{adv_id:\d+}", AdvView),
        web.delete(r"/advs/{adv_id:\d+}", AdvView),
        web.post(r"/adv", AdvView),
    ]
)

web.run_app(app, port=8080)
