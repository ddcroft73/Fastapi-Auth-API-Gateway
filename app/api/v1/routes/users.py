from typing import Any, List, Optional, Union
from datetime import datetime

from fastapi import (
    APIRouter, 
    Body, 
    Depends, 
    HTTPException, 
    Request
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse 
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas

from app.api import deps
from app.core.config import settings
from app.mail_utils import (
     verify_email, 
     generate_verifyemail_token
)

from app.utils.api_logger import logzz

router = APIRouter()


# api/v1/users/me
@router.get("/me", response_model=schemas.UserAccount)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    user_id: int = current_user.id
    account: models.Account = crud.account.get_by_user_id(db, user_id=user_id)

    user_data_encoded = jsonable_encoder(current_user)
    account_data_encoded = jsonable_encoder(account)
    return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)


# api/v1/
@router.get("/", response_model=List[schemas.UserAccount])
def read_users(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users: 
    Pull out all users in the system and return.

    This could get really slow when the users get into the 1000's need to think about this, a lot.
    """    
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    user_data: list[schemas.UserResp] = []

    for user in users:
        user_id: int = user.id
        account: models.Account = crud.account.get_by_user_id(db, user_id=user_id)
        user_data_encoded = jsonable_encoder(user)
        account_data_encoded = jsonable_encoder(account)

    return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)

# This will expect info for the User, and info for the users account. It will be sent in 
# api/v1/
@router.post("/", response_model=schemas.UserAccount)
def create_user(
    *, 
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    account_in: schemas.AccountCreate,
) -> Any:
    """
    Create new user. When a user registers, this endpoint creates the user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    try:        
        # add user, and then the users account info as it was passed in
        user: models.User = crud.user.create_no_commit(db, obj_in=user_in)
        account_in.user_id=user.id
        account: models.Account = crud.account.create_no_commit(db, obj_in=account_in)
                
        db.commit()
        db.refresh(user)
        db.refresh(account)
        
        # Prepare the response
        user_data_encoded = jsonable_encoder(user)
        account_data_encoded = jsonable_encoder(account)

        # notify New user they need to verify their Email if enabled.
        if settings.EMAILS_ENABLED and user_in.email:
           verify_email_token = generate_verifyemail_token(user_in.email)
           verify_email(
               email_to= user_in.email, 
               email_username=user_in.email, 
               token=verify_email_token
           )

        logzz.info(f"New User Created: {user_in.email}", timestamp=1)
        return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)
    
    except Exception as err:
        # incase of error make sure no data is saved. Dont want a user without an account and vice versa
        db.rollback()
        logzz.error(f"Endpoint -> api/v1 - create_user(): \n{str(err)} ")
    

# I will definitley need to alter this to update the acount info as well....
# I can pass in as many as i need to update
# api/v1/me
@router.put("/me", response_model=schemas.UserAccount)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    phone_number: str = Body(None),
    #Account
    subscription_type: str = Body(None),
    bill_renew_date: Union[datetime,str, None] = Body(None),
    auto_bill_renewal: bool = Body(None),
    cancellation_date: Union[datetime, str, None] = Body(None),
    cancellation_reason: str = Body(None),
    preferred_contact_method: str = Body(None),
    timezone: str = Body(None),

    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    try: 
        current_user_data = jsonable_encoder(current_user)
        current_users_account: models.Account = current_user.account
        #current_users_account = crud.account.get_by_user_id(db, user_id=current_user.id)
        user_account_data = jsonable_encoder(current_users_account)
        
        user_in = schemas.UserUpdate(**current_user_data)
        account_in = schemas.AccountUpdate(**user_account_data)
        
        logzz.info(f"user_account_data: {(user_account_data)}")
        logzz.debug(f"account_in: {(account_in)}")
   
        # parse the incoming data.
        if password is not None:
            user_in.password = password
        if full_name is not None:
            user_in.full_name = full_name
        if email is not None:
            user_in.email = email
        if phone_number is not None:  # Update for new field
            user_in.phone_number = phone_number
        
        if subscription_type is not None:
            account_in.subscription_type = subscription_type
        if bill_renew_date is not None:
            account_in.bill_renew_date = bill_renew_date
        if auto_bill_renewal is not None: 
            account_in.auto_bill_renewal = auto_bill_renewal
        if cancellation_date is not None:
            account_in.cancellation_date = cancellation_date
        if cancellation_reason is not None:
            account_in.cancellation_reason = cancellation_reason
        if preferred_contact_method is not None:
            account_in.preferred_contact_method = preferred_contact_method
        if timezone is not None:
            account_in.timezone = timezone

        user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
        account = crud.account.update(db, db_obj=current_users_account, obj_in=account_in)
        
        user_data_encoded = jsonable_encoder(user)
        account_data_encoded = jsonable_encoder(account)
        
        return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)
    
    except Exception as err:
        logzz.error(f"EndPoint -> api/v1/me 'update_user_me()': \n{str(err)}")


# api/v1/open
@router.post("/open", response_model=schemas.User)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
    phone_number: str = Body(None),
    is_verified: bool = Body(None),
    failed_attempts: int = Body(None),
    account_locked: bool = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    try:
        if not settings.USERS_OPEN_REGISTRATION:
            raise HTTPException(
                status_code=403,
                detail="Open user registration is forbidden on this server",
            )
        
        user = crud.user.get_by_email(db, email=email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system",
            )
        
        user_in = schemas.UserCreate(
            password=password,
            email=email, 
            full_name=full_name,
            phone_number=phone_number,
            is_verified=is_verified,
            failed_attempts=failed_attempts,
            account_locked=account_locked
        )
        
        user = crud.user.create(db, obj_in=user_in)

    except Exception as err:
        logzz.error(f"An error occured in 'create_user_open()': \n{str(err)}")

    return user

# THis endpoint will need to be altered to return all the data including the account info
#/api/v1/users/{user_id}
@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, model_id=user_id)
    if user == current_user:
        return user
    
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    
    return user

# THis endpoint is to update another user by admin. I will need to make special sckema that encompasses
# user and account info

#/api/v1/users/{user_id}
@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    SuperUser action. 
    """
    user = crud.user.get(db, model_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
