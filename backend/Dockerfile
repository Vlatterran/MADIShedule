FROM python:3.10-slim-buster

COPY requirements.txt backend/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

COPY . backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


CMD uvicorn backend.main:app --host 0.0.0.0 --port 8000