FROM python:3.12-alpine
RUN apk add --no-cache gcc musl-dev linux-headers 
RUN apk add --no-cache curl

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /backend

# Копируем файл с зависимостями
COPY ./requirements.txt ./requirements.txt
# Устанавливаем зависимости
# RUN pip3 install -r requirements.txt
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --default-timeout=100 \
    -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Указываем порт, который будет использовать приложение
EXPOSE 8080

# Команда для запуска сервера

CMD ["python3", "server.py"]

