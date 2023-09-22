from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import  Any
from app import models, schemas, crud
from sqlalchemy.orm import Session
from app.api import deps
from background_tasks.tasks import celery_task
from app.utils.api_logger import logzz
from sqlalchemy.orm import joinedload

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


@router.put("/test-update-me/", response_model=schemas.UserAccount)
def test_update_code(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    # Endpoint to test and hopefully learn why my models.Account ORM is not being populated with any data.
    # and possibly try out some raw SQL queries ans see id I can get the account table to update.
    # 
    # try to update the cancellation date and reason for the current user. This data resides in the account table,
    # so we dont have any reason to update user.

    # This works, crazy enough. works as expected with great results. 
    # Solution, update and encode the users data, and then the account in seperate DB interactions.
    # It was that easy. 

    # User Data update
    user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**user_data)
    user_in.full_name = "John MichaelSon"
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    user_update = jsonable_encoder(user)

    # Account Data Update
    current_users_account: models.Account = current_user.account
    account_data = jsonable_encoder(current_users_account)
    account_in = schemas.AccountUpdate(**account_data)

    account_in.cancellation_date = "09/23/2023"
    account_in.cancellation_reason = "The endpoint for testing works if Split Up Again"

    account = crud.account.update(
        db, db_obj=current_users_account, obj_in=account_in)
    account_update = jsonable_encoder(account)
    
        
    return schemas.UserAccount(user=user_update, account=account_update)
