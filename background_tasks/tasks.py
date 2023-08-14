from .celery_app import celery_app
from time import sleep

#
# I could utilize celery beat to set a timer for the failed attempts at login. 
# I could utilize celery to do database operatioins as well. 
# As this API grows this may be key... 
#

@celery_app.task()
def celery_task(arg: str):
    sleep(10)
    print(f"The arg is: {arg}")
    return True