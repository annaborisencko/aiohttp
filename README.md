# Aiohttp Server Project

## Описание

Проект представляет собой веб-сервер на базе aiohttp.

## Требования

- Docker
- Docker Compose
- Git
- Python

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/annaborisencko/aiohttp.git
cd aiohttp
```

### 2. Настройка переменных окружения

Скопируйте файл .env.example в .env и заполните его необходимыми данными:

```bash
cp .env.example .env
```

Отредактируйте файл .env в любом текстовом редакторе.

```bash
nano .env
```

### 3. Запуск Docker контейнеров

Запустите все сервисы с помощью Docker Compose:

```bash
docker-compose up -d
```

Проверьте, что оба контейнера запущены и работают:

```bash
docker-compose ps
```

Вы должны увидеть два контейнера:

PROJECT_NAME-db - контейнер с PostgreSQL
PROJECT_NAME-app - контейнер с aiohttp сервером

### 4. Выполнение клиентского скрипта

После успешного запуска контейнеров выполните клиентский скрипт:

```bash
docker-compose exec PROJECT_NAME-app python client.py
```

Или, если используете Python 3:

```bash
docker-compose exec PROJECT_NAME-app python3 client.py
```

Результат выполнения отобразится в терминале.

### 5. Остановка контейнеров

После проверки работы, остановите контейнеры

```bash
docker-compose down -v
```