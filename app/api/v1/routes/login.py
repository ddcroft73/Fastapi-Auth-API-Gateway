from datetime import timedelta, datetime
from typing import Any, Union, Optional, Annotated
import string
from random import randint , choice

from fastapi import (
    APIRouter, 
    Body,
    Depends,
    HTTPException, 
    Request, 
    Query
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from pydantic.networks import EmailStr
from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.utils.api_logger import logzz
from app.core.security import get_password_hash
from app.mail_utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
    verify_emailVerify_token,
    generate_verifyemail_token,
    verify_email as Verify_Email # Alias so it doesnt call the loacl 
)                                # function by the same name. I just ran out of ways to say verify email

router = APIRouter()

#
#/api/v1/auth/login/access-token
#
@router.post("/login/access-token", response_model=Union[schemas.Token, schemas.TwoFactorAuth])
async def login_access_token(
    request: Request,
    db: Annotated[Session, Depends(deps.get_db)], 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    WHen a user logs in, an access token is generated and returned if the credintials
    check out. The user will not have to login again until the token expires
    """
    def save_login_information() -> None:
        '''
          Nested helper to mark user as logged in. 
        '''
        current_time: str = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        account = models.Account = user.account #crud.account.get_by_user_id(db, user_id=user.id)

        account.last_login_date = current_time
        user.is_loggedin = True

        db.add(user)
        db.add(account)
        db.commit()
        

        user_data = {
            'username': form_data.username,
            'time_in' : current_time,
            'ip_address': request.client.host
        }
        
        logzz.login(
            user_data, heading="New Login"
        ) 
     

    user: models.User = crud.user.authenticate(db, 
        email=form_data.username, 
        password=form_data.password
    )        
     # This is also true if the user does not exist...
    if not user:
        raise HTTPException(
            status_code=401, detail="wrong credentials"
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=401, detail="inactive user"
        )
    elif not crud.user.is_verified(user):
        logzz.info(f"{user.email} attempted a login before verification.")
        raise HTTPException(
            status_code=401, detail="non-verified"
        )    
    '''elif crud.user.is_account_locked(user):
        raise HTTPException(status_code=403, detail="locked out")'''
    
    save_login_information()    

    if crud.user.is_superuser(user):
          user_role ='admin'
    else: user_role = 'user'
    
    # BRANCH Off to handle 2FA
    if user.account.use_2FA:      
        token_2FA: schemas.TwoFactorAuth = await security.send_2FA_code(    
            user_id=user.id, 
            user_email=user.email, 
            user_phone_number=user.phone_number,  
            provider=user.cell_provider,
            contact_method_2FA=user.account.contact_method_2FA,
            user_role=user_role
        )   
        return schemas.TwoFactorAuth(
            code=token_2FA.code, token=token_2FA.token, user_role=user_role
        )    
    
    # No 2Fa, issue the token
    access_token_expires: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)      
    access_token: str = security.create_access_token(
        subject=user.id, user_role=user_role, expires_delta=access_token_expires
    )

    return schemas.Token(
        access_token=access_token, token_type="bearer", user_role=user_role
    )
        

#/api/v1/auth/login/verify-admin-pin/    http://192.168.12.189:8015/api/v1/auth/login/verify-admin-pin?pin_number=111111
@router.post("/login/verify-admin-pin", response_model=schemas.AdminToken)
def verify_admin_pin(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    pin_number: str = Query(...),
) -> Any:     

    # Is this even an ADMIN? 
    if not crud.user.is_superuser(current_user):
        logzz.info(f"User: {current_user.email} is trying to access the admin area.", timestamp=1)
        raise HTTPException(
            status_code=403,
            detail="You don't have the priveleges to be here."
        )
        
    admin: models.Account = crud.account.check_PIN(
        db,
        pin=pin_number, 
        user_id=current_user.account.user_id
    )    

    if not admin:
        raise HTTPException(
            status_code=401, detail="wrong pin number"
        )
    
    admin_token_expires: timedelta = timedelta(minutes=settings.ADMIN_TOKEN_EXPIRE_MINUTES)  
    admin_token: str = security.create_admin_token(
        subject=admin.user.email, 
        expires_delta=admin_token_expires
    )
    logzz.info(f"An Admin token was generated for: {admin.user.email}", timestamp=True)
    return schemas.AdminToken(token=admin_token)

#
#/api/v1/auth/login/test-token
#
@router.post("/login/test-token", response_model=schemas.UserAccount)
def test_token(
    current_user: Annotated[models.User, Depends(deps.get_current_user)]
) -> Any:
    """
    Test access token
    """
    logzz.info(f"Token tested for: {current_user.email}", timestamp=True)

    return schemas.UserAccount(
        user=jsonable_encoder(current_user), 
        account=jsonable_encoder(current_user.account)
    ) 


#
#/api/v1/auth/password-recovery/{email}
#
@router.post("/password-recovery/{email}", response_model=schemas.Msg)
async def recover_password(
    email: str, 
    db: Annotated[Session, Depends(deps.get_db)]) -> Any:
    """
    Password Recovery:
    If the user is in the system,  Then they will be
    sent an email with instructions on how to change their password.
    """
    user: models.User = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User does not exist",
        )        
    
    password_reset_token = generate_password_reset_token(email=email)

    await send_reset_password_email(
        email_to=user.email, email_username=email, token=password_reset_token
    )
    logzz.info(f"A password recovery is in progress for: {email}. An email has been dispatched.")
    return {
        "msg": f"A password recovery email has been sent to {email}."
    }


#
#/api/v1/auth/reset-password/
#
@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Query(...),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password:
    A user has changed their password, If the token they are using is valid and 
    they ae in the system, The password willl be changed. 
    """
    email: Optional[EmailStr] = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=403, detail="Invalid Token"
        )    
    user: models.User = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User: {email} does not exist on this system.",
        )        
    if not crud.user.is_active(user):
        raise HTTPException(
            status_code=401, 
            detail=f"User: {email} has been deactivated. "
                    "Contact support; support@lifepackage.net for more information."
        )
    
    hashed_password: str = get_password_hash(new_password)
    user.hashed_password = hashed_password

    db.add(user)
    db.commit()

    logzz.info(f'User: {email} has changed their password.', timestamp=True)
    return {
        "msg": f"User: {email} has successfully updated their password."
    }



@router.put("/resend-verification/", response_model=schemas.Msg)
async def resend_verification(email: EmailStr = Query(...)):
    email_token: str = generate_verifyemail_token(email)
    
    await Verify_Email(
        email_to=email, 
        email_username=email,
        token=email_token
    )

    logzz.info(f'User: {email} was sent another verify email token.', timestamp=True)
    return {
        "msg": f"Email verification Re-sent to: {email}. "
    }



@router.get("/verify-email/", response_model=schemas.Msg)
def verify_email(
    token: str = Query(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    '''
      If all checks out, change is_verified to True.
    '''
    email: Optional[str] = verify_emailVerify_token(token)
    if not email:
        raise HTTPException(
            status_code=401, detail="Invalid Token"
        )    
    user: models.User = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail="User doesn't exist...",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=401, detail="Account is inactive..."
        )
    
    user.is_verified = True    
    
    db.add(user)
    db.commit()    

    logzz.info(f'Email verified for: {user.email}', timestamp=True)
    return {"msg": "Email Verified. User Ok to login"}


#
#  LOG_OUT USER by user_id
#
@router.put("/logout/{user_id}", response_model=schemas.UserAccount)
def logout_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    superuser: models.User = Depends(deps.get_current_active_superuser),
    admin_token: str = Body(..., embed=True) 
) -> Any:
    '''
      Admin Action. Log out a given user.
    '''    
    admin: bool = security.verify_admin_token(admin_token)
    if not admin:
        raise HTTPException(
            status_code=401, detail="invalid admin token"
        )
    
    user: models.User = crud.user.get(db, model_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"user does not exist"
        )

    user.is_loggedin = False
    db.add(user) 
    db.commit()
    
    return schemas.UserAccount(
        user=jsonable_encoder(user), 
        account=jsonable_encoder(user.account)
    ) 


@router.put("/2FA/verify-2FA-code/", response_model=schemas.Token)
def verify_2FA_code(
    *,
    db: Session = Depends(deps.get_db),
    code_2FA: str = Body(...),
    code_user: str = Body(...), 
    email_account: str = Body(...),
    timed_token: str = Body(...),    
) -> Any:
    '''
      Verifies the code the user input for 2FA.  And issues an Access token
      on success.
    '''    
    user_role: str 
    
    token_expired: bool = security.verify_token(timed_token)
    if not token_expired:
        raise HTTPException(
            status_code=401, detail="10 minutes. Token expired."
        )     
    token_user: Optional[EmailStr] = security.email_from_token(timed_token)
    if not token_user == email_account:
        raise HTTPException(
            status_code=401, detail="Invalid email."
        )
    good_code: bool = security.verify_2FA(code_2FA, code_user)
    if not good_code:
        raise HTTPException(
            status_code=401, detail="Codes do not match."
        )

    user: models.User = crud.user.get_by_email(db, email=email_account)
    if crud.user.is_superuser(user):
        user_role ='admin'
    else:
        user_role = 'user'

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    return {
        "access_token": security.create_access_token(
            subject=user.id, user_role=user_role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user_role": user_role
    }
    


@router.put("/2FA/resend-2FA-code/", response_model=schemas.TwoFactorAuth)
async def resend_2FA_code(
    *,
    db: Session = Depends(deps.get_db),
    email: str = Query(...) ,
) -> Any:
    
    user: models.User = crud.user.get_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=404, detail="user does not exist"
        )
    
    user_role: str = "admin" if crud.user.is_superuser(user) else "user"

    token_2FA: schemas.TwoFactorAuth = await security.send_2FA_code(    
        user_id=user.id, 
        user_email=user.email, 
        user_phone_number=user.phone_number,  
        contact_method_2FA=user.account.contact_method_2FA,
        user_role=user_role
    )    
    
    msg: str = f"2FA code resent to: {email if user.account.contact_method_2FA == 'email' else user.phone_number}" 
    logzz.info(msg, timestamp=1)

    return schemas.TwoFactorAuth(
        code=token_2FA.code, token=token_2FA.token, user_role=user_role
    )
