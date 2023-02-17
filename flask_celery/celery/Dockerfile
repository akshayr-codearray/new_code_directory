FROM python:3.8-buster

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ENTRYPOINT celery -A app.celery worker --loglevel=info
