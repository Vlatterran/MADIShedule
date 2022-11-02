FROM python:3.10

COPY . backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

CMD uvicorn backend.main:app --host 0.0.0.0 --port 8000