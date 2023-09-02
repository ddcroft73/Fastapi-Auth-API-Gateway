#
# This is crazy to me..... On my laptop this setup works great. Creating a user to run the celery worker that hasnt 
# root priveledges. However on my desktop WSL2, it will not work. It constantly tells me it cant access celery.log becuase
# it hasnt the priveledges. so fuck it. root it is on te desktop!!!

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

# NOTE: When using this file, I can;t get permission to celery.log. I created a user without su priveledges
# that used to work perfetly, now it says
# PermissionError: [Errno 13] Permission denied: '/app/logs/celery.log' Need to figure out what has chcnged.
# Meantime, use backend.dockerfile and run celery with su priveledges

RUN chown -R celery_user:celery_user /app
RUN chown -R celery_user:celery_user /app/logs/celery.log
USER celery_user

