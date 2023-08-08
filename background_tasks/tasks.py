from .celery_app import celery_app
from time import sleep

@celery_app.task()
def celery_task(arg: str):
    sleep(10)
    print(f"The arg is: {arg}")
    return True