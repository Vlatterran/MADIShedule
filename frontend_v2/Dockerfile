FROM python:3.10-slim-buster

COPY requirements.txt frontend/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r frontend/requirements.txt


COPY . frontend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV STATIC_FILES_PATH "frontend/static"


CMD uvicorn frontend.main:app --host 0.0.0.0 --port 8000