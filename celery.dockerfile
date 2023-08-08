FROM python:3.11.2-slim-buster

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Need to create a user without superuser priveledges to run celery, hence a seperate 
# dockerfilez and dedicated user.
RUN useradd -m celery_user
RUN chown -R celery_user:celery_user /app
USER celery_user

