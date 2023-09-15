from typing import Any, List, Optional
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

# api/v1/
@router.get("/", response_model=List[schemas.User])
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
    """    
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    # this may need to return account data as well... I may need to create a new scema to pull it all together
    # I could just leave thisas is or make it even less.... this ocould just be a litttle info about each user and then
    # to dig deeper on an individual user. 
    return users

# This will expect info for the User, and info for the users account. It will be sent in 
# api/v1/
@router.post("/", response_model=schemas.User)
def create_user(
    *, 
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    admin_pin: str = None
) -> Any:
    """
    Create new user.
    When a user registers, this endpoint creates the user.
    """
    current_date: datetime = datetime.today()
    formatted_date_today: str = current_date.strftime('%m/%d/%Y')

    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )    
    # set up the users account with default data
    account_in = schemas.AccountCreate(
        account_creation_date=formatted_date_today,
        last_login_date=formatted_date_today,
        bill_renew_date=formatted_date_today,
        last_account_changes_date=formatted_date_today,
        account_last_update_date=formatted_date_today,
        admin_PIN=admin_pin
    )

    try:
        # Create the user and add data the appropriate data to the User Table in the DB
        user: schemas.User = crud.user.create(db, obj_in=user_in)
        # create the account data 
        account: schemas.Account = crud.account.create(db, obj_in=account_in)

        logzz.info(f"New User Created: {user_in.email}", timestamp=1)

        if settings.EMAILS_ENABLED and user_in.email:
           verify_email_token = generate_verifyemail_token(user_in.email)
           verify_email(
               email_to='lapddc73@gmail.com',# user_in.email, HARD CODED FOR testing
               email_username=user_in.email, 
               token=verify_email_token
            )
            
    except Exception as err:
        logzz.error(f"Endpoint -> api/v1 - create_user(): \n{str(err)} ")

    return user

# I will definitley need to alter this to update the acount info as well....
# I can pass in as many as i need to update
# api/v1/me
@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    phone_number: str = Body(None),
    is_verified: bool = Body(False),
    failed_attempts: int = Body(None),
    account_locked: bool = Body(False),
    # Account Info a user can update

    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    try: 
        current_user_data = jsonable_encoder(current_user)
        user_in = schemas.UserUpdate(**current_user_data)

        if password is not None:
            user_in.password = password
        if full_name is not None:
            user_in.full_name = full_name
        if email is not None:
            user_in.email = email
        if phone_number is not None:  # Update for new field
            user_in.phone_number = phone_number
        if is_verified is not None:  # Update for new field
            user_in.is_verified = is_verified
        if failed_attempts is not None:  # Update for new field
            user_in.failed_attempts = failed_attempts
        if account_locked is not None:  # Update for new field
            user_in.account_locked = account_locked

        user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
        
        # Now Account data
    except Exception as err:
        logzz.error(f"EndPoint -> api/v1/me 'update_user_me()': \n{str(err)}")

    return user



# api/v1/users/me
@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


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


## Endpoint to look up user bt Email