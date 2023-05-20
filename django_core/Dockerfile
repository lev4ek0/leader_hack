# получаем image для нашего питона
FROM python:3.10

# задаём переменные окружения, чтобы
# предотвратить ряд событий, а именно:
# создания .pyc файлов и использования
# питоном буффера для stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# обновляем  репозитории
RUN apt-get update -y && apt-get upgrade -y

# ставим зависимости GDAL, PROJ для PostGis
RUN apt-get install -y gdal-bin libgdal-dev
RUN apt-get install -y python3-gdal
RUN apt-get install -y binutils libproj-dev

# ставим локализацию
RUN apt-get install -y gettext

# устанавливаем рабочую директорию
WORKDIR /django_core

# ставим python зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# копируем проект
COPY . .
