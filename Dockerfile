FROM python:3.9-buster

RUN apt-get update \
    && apt-get install -y \
    curl \
    libxrender1 \
    libjpeg62-turbo \
    fontconfig \
    libxtst6 \
    xfonts-75dpi \
    xfonts-base \
    xz-utils
RUN curl "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb" -L -o "wkhtmltopdf.deb"

RUN dpkg -i wkhtmltopdf.deb

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#Original section
RUN mkdir /code

WORKDIR /code

RUN pip install --upgrade pip
COPY requirements.txt /code/

RUN pip install -r requirements.txt
COPY . /code/
# COPY contracts /code/

EXPOSE 8000

CMD ["uvicorn", "FinCover.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "2","--log-level", "debug"]