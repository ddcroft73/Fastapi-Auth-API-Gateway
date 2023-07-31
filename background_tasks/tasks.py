from .celery_app import celery_app

@celery_app.task()
def celery_task(arg: str):
    print(f"The arg is: {arg}")
    return True