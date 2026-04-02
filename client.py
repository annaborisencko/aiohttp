import asyncio

import aiohttp

username = "Укажите имя пользоваетля"
password = "Укажите пароль пользователя"


async def main():

    async with aiohttp.ClientSession() as session:

        #################################################

        print("##### Регистрируем пользователя ######")
        response = await session.post(
            "http://0.0.0.0:8080/user",
            json={"name": username, "password": password},
        )
        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Получаем токен ######")
        response = await session.post(
            "http://0.0.0.0:8080/login", json={"name": username, "password": password}
        )

        json_response = await response.json()
        token_1 = json_response.get("token")
        print(response.status, "\n")

        #################################################

        print("##### Создаем объявление ######")
        response = await session.post(
            "http://0.0.0.0:8080/adv",
            json={
                "title": "Продам огурцы",
                "description": "Самые свежие огурцы на свете",
            },
            headers={
                "Authorization": f"Bearer {token_1}",
            },
        )
        json_response = await response.json()
        adv_id_1 = json_response.get("id")
        print(response.status, json_response, "\n")

        #################################################

        print("##### Просматриваем объявление ######")
        response = await session.get(f"http://0.0.0.0:8080/advs/{adv_id_1}")
        print(await response.json(), "\n")

        #################################################

        print("##### Меняем свое объявление ######")
        response = await session.patch(
            f"http://0.0.0.0:8080/advs/{adv_id_1}",
            json={
                "title": "Продам огурцы 1",
                "description": "Самые свежие огурцы на свете",
            },
            headers={
                "Authorization": f"Bearer {token_1}",
            },
        )
        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Просматриваем измененное объявление ######")
        response = await session.get(f"http://0.0.0.0:8080/advs/{adv_id_1}")
        print(await response.json(), "\n")

        #################################################

        print("##### Регистрируем второго пользователя ######")
        username_1 = f"{username}_1"
        password_1 = f"{password}_2"

        response = await session.post(
            "http://0.0.0.0:8080/user",
            json={"name": username_1, "password": password_1},
        )
        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Получаем токен для второго пользователя ######")

        response = await session.post(
            "http://0.0.0.0:8080/login",
            json={"name": username_1, "password": password_1},
        )

        json_response = await response.json()
        token_2 = json_response.get("token")
        print(response.status, "\n")

        #################################################

        print("##### Создаем второе объявление ######")

        response = await session.post(
            "http://0.0.0.0:8080/adv",
            json={
                "title": "Продам помидоры",
                "description": "Самые свежие помидоры на свете",
            },
            headers={
                "Authorization": f"Bearer {token_2}",
            },
        )
        json_response = await response.json()
        adv_id_2 = json_response.get("id")
        print(response.status, json_response, "\n")

        #################################################

        print("##### Меняем чужое объявление ######")
        response = await session.patch(
            f"http://0.0.0.0:8080/advs/{adv_id_1}",
            json={
                "title": "Продам огурцы 1",
                "description": "Самые свежие огурцы на свете",
            },
            headers={
                "Authorization": f"Bearer {token_2}",
            },
        )
        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Удаляем чужое объявление ######")
        response = await session.delete(
            f"http://0.0.0.0:8080/advs/{adv_id_1}",
            headers={
                "Authorization": f"Bearer {token_2}",
            },
        )
        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Удаляем свое объявление ######")
        response = await session.delete(
            f"http://0.0.0.0:8080/advs/{adv_id_2}",
            headers={
                "Authorization": f"Bearer {token_2}",
            },
        )
        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Получаем токен для неизвестного пользователя ######")

        response = await session.post(
            "http://0.0.0.0:8080/login",
            json={"name": f"wrong_{username_1}", "password": password_1},
        )

        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

        print("##### Получаем токен для пользователя с неправильным паролем ######")

        response = await session.post(
            "http://0.0.0.0:8080/login",
            json={"name": username_1, "password": f"wrong_{password_1}"},
        )

        json_response = await response.json()
        print(response.status, json_response, "\n")

        #################################################

asyncio.run(main())
