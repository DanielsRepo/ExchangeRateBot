FROM python:3.8

WORKDIR /bot

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p ./bot/tmp

RUN pip install --upgrade pip && \
    pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --system

COPY . .
