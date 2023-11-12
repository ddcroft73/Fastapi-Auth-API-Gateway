from typing import Any, List, Optional, Union
from datetime import datetime
from time import sleep

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
from app.core import security
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
    account: models.Account = crud.account.get_by_user_id(db, user_id=current_user.id)

    user_data_encoded = jsonable_encoder(current_user)
    account_data_encoded = jsonable_encoder(account)    
    
    return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)

# api/v1/users/
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
    user_data: list[schemas.UserAccount] = []

    for user in users:        
        account: models.Account = user.account
        user_data_encoded = jsonable_encoder(user)
        account_data_encoded = jsonable_encoder(account)

        user_data.append(schemas.UserAccount(
            user=user_data_encoded, 
            account=account_data_encoded)
        )

    return user_data 


# get user by email
@router.get("/user-by/{email}", response_model=schemas.UserAccount)
def user_by_email( 
    *,
    db: Session = Depends(deps.get_db),
    super_user: models.User = Depends(deps.get_current_active_superuser),
    email: str,   
    admin_token: str = Body(..., embed=True) 
) -> Any:
    '''
    Get a user by their email.

    d3d
    '''
    if not security.verify_admin_token(admin_token):
        raise HTTPException(status_code=400, detail="Invalid Token")
    
    user = crud.user.get_by_email(db,email=email)
    if not user:
        raise HTTPException(status_code=400, detail=f"No user: {email} in this system.")
    
    account = user.account 
    user_data_encoded = jsonable_encoder(user)
    account_data_encoded = jsonable_encoder(account)
    
    return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)

# This will expect info for the User, and info for the users account. It will be sent in 
# api/v1/
@router.post("/registration", response_model=schemas.UserAccount)
async def user_registration(
    *, 
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    account_in: schemas.AccountCreate,
) -> Any:
    """
    New User Registration.

    """

    if not settings.USERS_OPEN_REGISTRATION:
            raise HTTPException(
                status_code=403,
                detail="Open user registration is forbidden for now.",
            )
    
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    try:        
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
           verify_email_token: str = generate_verifyemail_token(user_in.email)

           await verify_email(
               email_to=user_in.email, 
               email_username=user_in.email, 
               token=verify_email_token
           )

        logzz.info(f"New User Created: {user_in.email}", timestamp=1)
        return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)
    
    except Exception as err:
        # incase of error make sure no data is saved. Dont want a user without an account and vice versa
        db.rollback()
        logzz.error(f"Endpoint -> api/v1 - create_user(): \n{str(err)} ")


#
# api/v1/users/me update own user
# 
@router.put("/me", response_model=schemas.UserAccount)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    #User
    password: str = Body(None),
    full_name: str = Body(None),
    cell_provider: str = Body(None),
    phone_number: str = Body(None),
    #Account
    subscription_type: str = Body(None),
    bill_renew_date: Union[datetime,str, None] = Body(None),
    auto_bill_renewal: bool = Body(None),
    cancellation_date: Union[datetime, str, None] = Body(None),
    cancellation_reason: str = Body(None),
    preferred_contact_method: str = Body(None),
    admin_PIN: str = Body(None),
    timezone: str = Body(None),
    use_2FA: bool = Body(None),
    contact_method_2FA: str = Body(None),
    cell_provider_2FA: str = Body(None),    
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update own user.
    """
    try: 
        # Handle User instance
        current_user_data = jsonable_encoder(current_user)        
        user_in = schemas.UserUpdate(**current_user_data)   
        # parse the incoming data.
        if password is not None:
            user_in.password = password
        if full_name is not None:
            user_in.full_name = full_name        
        if cell_provider is not None:
            user_in.cell_provider = cell_provider
        if phone_number is not None:  # Update for new field
            user_in.phone_number = phone_number

        user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
        user_data_encoded = jsonable_encoder(user)

        # Handle Account Instance.
        current_users_account: models.Account = crud.account.get_by_user_id(db, user_id=user.id) #current_user.account
        user_account_data = jsonable_encoder(current_users_account)
        account_in = schemas.AccountUpdate(**user_account_data)

        # parse Account fields to update
        if admin_PIN is not None:
            account_in.admin_PIN = admin_PIN            
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

        if use_2FA is not None:
            account_in.use_2FA = use_2FA
        if contact_method_2FA is not None:
            account_in.contact_method_2FA = contact_method_2FA
        if cell_provider_2FA is not None:
            account_in.cell_provider_2FA = cell_provider_2FA

        account = crud.account.update(db, db_obj=current_users_account, obj_in=account_in)   
        account = crud.account.update(db, db_obj=current_users_account, obj_in=account_in)        
        account_data_encoded = jsonable_encoder(account)
        
        return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)
    
    except Exception as err:
        logzz.error(f"EndPoint -> api/v1/users/me 'update_user_me()': \n{str(err)}")


#/api/v1/users/update/{user_id}

#NEED figure out why the second update (account) does not save. User only saves, and account will if i change the order
# and then user will not...
@router.put("/update/{user_id}", response_model=Union[schemas.UserAccount, schemas.Msg])
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    account_in: schemas.AccountUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser), 
    admin_token: str = Body(..., embed=True)
) -> Any:
    """
    Update a user. SuperUser action. 
    """
    try:
        if not security.verify_admin_token(admin_token):
            raise HTTPException(status_code=403, detail="Admin token invalid")    
        
        user = crud.user.get(db, model_id=user_id)
        account = crud.account.get_by_user_id(db, user_id=user.id)#user.account
        
        if user == None or account == None:
            return {"msg": "That user account does not exist."}
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="The user with this username does not exist in the system",
            )
        
        user_after_update = crud.user.update(db, db_obj=user, obj_in=user_in) 
        user_data_encoded = jsonable_encoder(user_after_update)       
         
        # Hack to fix the Update Bug... update the second addition to the DB twice. In this case I am 
        # trying to update account after user. So I need to run update twice on account. 
        # Im sure I don't know the exact reason this is needed, but this fixes it. I'll spend
        # time on this in the future.      
        account_after_update = crud.account.update(db, db_obj=account, obj_in=account_in)  
        account_after_update = crud.account.update(db, db_obj=account, obj_in=account_in)   

        account_data_encoded = jsonable_encoder(account_after_update)
        return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)

    except Exception as exc:
        logzz.error(str(exc))

# api/v1/create/
@router.post("/create", response_model=schemas.UserAccount)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    account_in: schemas.AccountCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    admin_token: str = Body(..., embed=True)
) -> Any:
    """
    Create new user by admin
    """
    try:
        if not settings.USERS_OPEN_REGISTRATION:
            raise HTTPException(
                status_code=403,
                detail="Open user registration is forbidden on this server",
            )
        
    # code to create a user. This is where admin would create a superUser. 
    # Actually a su can becreated in either endpoint. all it takes is 
    # is_superuser = True, that's it. Do I need 2 seperate ones? I guess yes becasue
    # witht he other I can turn it on and off so that users cant openly reister.
    # Only I can create them.
    # 
    # Could prove useful if someting goes wrong.   
    
    except Exception as err:
        logzz.error(f"An error occured in 'create_user_open()': \n{str(err)}")


#/api/v1/users/{user_id}
@router.get("/{user_id}", response_model=Union[schemas.UserAccount, schemas.Msg])
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    We need to return The User and acount info
    """
    user = crud.user.get(db, model_id=user_id)
    account: models.Account = crud.account.get_by_user_id(db, user_id=user_id)
    
    user_data_encoded = jsonable_encoder(user)
    account_data_encoded = jsonable_encoder(account)

    if user == None and account == None:
        return {"msg": "That record does not exist"}
    if user == None or account == None:
        return {"msg": "Either user or account are corrupt."}

    return schemas.UserAccount(user=user_data_encoded, account=account_data_encoded)        
    
 

@router.delete("/delete/{user_id}", response_model=schemas.Msg)
def delete_user(
    user_id: int,
    current_superuser: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
    admin_token: str = Body(..., embed=True)
) -> Any:
    '''
    Delete a user from the system. Super user action.
    '''
    
    if not security.verify_admin_token(admin_token):
        raise HTTPException(status_code=403, detail="Admin token invalid")    
    
    user = crud.user.get(db, model_id=user_id)

    if not user:
        raise HTTPException(
                status_code=404,
                detail="The user with this username does not exists in the system",
            )
    
    crud.user.remove(db, model_id=user_id)
    logzz.info(f"Deleted user: {user.email}", timestamp=True)
    return {"msg": f"Deleted user: {user.email}"}