import bcrypt
import jwt
import time
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")


def generate_token(user_id: int, expires_in: int = 600) -> str:
    """Функция для создания токена"""
    json_password = {"user_id": user_id, "exp": time.time() + expires_in}

    return jwt.encode(json_password, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """Функция для проверки токена"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        print(f"Decode error: {e}")
        return None


def hash_password(password: str) -> str:
    """Функция для хэширования пароля"""
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


def verify_password(json_password: str, hashed_password: str) -> bool:
    """Функция для проверки пароля"""
    return bcrypt.checkpw(json_password.encode(), hashed_password.encode())
