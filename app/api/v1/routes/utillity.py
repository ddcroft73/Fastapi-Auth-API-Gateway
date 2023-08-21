from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from typing import  Any
from app import models, schemas
from app.api import deps
from background_tasks.tasks import celery_task

router = APIRouter()

# This is to be used test, and for misc purposed yet to be determined

@router.get("/test-celery{var}", response_model=schemas.Msg)
def test_celery(
    var: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery: 
    Run the current celery task to make sure its working. will only proceed if 
    this user is a current active superuser. 
    """
    celery_task.delay(var)
    return {"msg": "Task Initiated."}