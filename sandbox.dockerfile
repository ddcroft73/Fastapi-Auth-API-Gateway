FROM python:3.11.2-slim-buster

WORKDIR /sandbox

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

RUN pip install --upgrade pip
COPY app/sandbox/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app/sandbox/ .