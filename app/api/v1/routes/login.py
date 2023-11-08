from datetime import timedelta, datetime
from typing import Any, Union, Optional
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
from app.core.security import get_password_hash, generate_singleuse_token
from app.mail_utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
    verify_emailVerify_token,
    generate_verifyemail_token,
    verify_email,
    send_email,
    send_sms
)
from app.email_templates.email_2FA_code import build_template_2FA_code

router = APIRouter()

#
#/api/v1/auth/login/access-token
#
@router.post("/login/access-token", response_model=Union[schemas.Token, schemas.Msg])
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    WHen a user logs in, an access token is generated and returned if the credintials
    check out. The user will not have to login again until the token expires
    """
    def save_login_information() -> None:
        current_time = str = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        account = models.Account = crud.account.get_by_user_id(db, user_id=user.id)

        account.last_login_date = current_time
        user.is_loggedin = True

        db.add(user)
        db.add(account)
        db.commit()

    user_role: str

    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    if crud.user.is_superuser(user):
         user_role ='admin'
    else:
        user_role = 'user'

    save_login_information()    

    # Is this user using 2FA? If so don;t send back the token... send back a message to let the client
    # know to invoke the 2FA.
    if user.account.use_2FA: 
        pass
        #return schemas.Msg(msg="use_2FA")

    # The client gets the msg to invoke 2FA, the client sends a request to this server @ get-2fa-code/
    # a code is generated and sent to the user either by EMail, SMS. and the client will call the UI
    # component to take the users code input. the code is then sent back to this server @ verify-2fa-code/
    # If theu match THEN the token is generat3ed, and sent back to the client. 
    token: str = security.create_access_token(user.id, user_role, expires_delta=access_token_expires)
    return schemas.Token(access_token=token, token_type="bearer")
        

#
#/api/v1/auth/login/test-token
#
@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """

    return current_user
#
#/api/v1/auth/login/password-recovery/{email}
#
@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery:
    If the user is in the system,  Then they will be
    sent an email with instructions on how to change their password.
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )    
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return JSONResponse({"msg": "Password recovery email sent"})

#
#/api/v1/auth/reset-password/
#
@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Query(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password:
    A user has changed their password, If the token they are using is valid and 
    they ae in the system, The password willl be changed. 
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password

    db.add(user)
    db.commit()
    logzz.info(f'User: {email} changed password.', timestamp=True)
    return JSONResponse({"result": "Password updated successfully."})



@router.get("/verify-email/", response_model=schemas.Msg)
def verify_email(
    token: str = Query(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    '''
      If all checks out, change is_verified to True.
    '''
    email =  verify_emailVerify_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    user.is_verified = True
    
    db.add(user)
    db.commit()    
    logzz.info(f'Email verified for: {user.email}', timestamp=True)
    return JSONResponse({"result": "Email Verified. User Ok to login"})


@router.put("/resend-verification/", response_model=schemas.Msg)
def resend_verification(email: EmailStr = Query(...)):
    # Create a new token and send out
    email_token = generate_verifyemail_token(email)
    verify_email(
        email_to='gen.disarray73@outlook.com',  # user_in.email, HARD CODED FOR testing
        email_username=email,
        token=email_token
    )
    logzz.info(f'User: {email} was sent another verify email token.', timestamp=True)
    return {"msg": "Resend email verification."}

#
#  LOG_OUT USER by user_id
#
@router.put("/logout/{user_id}", response_model=schemas.UserAccount)
def logout_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_superuser: models.User = Depends(deps.get_current_active_superuser),
    admin_token: str = Body(..., embed=True) 
) -> Any:
    '''
      Admin Action. Log out a given user.
    '''    
    if not security.verify_admin_token(admin_token):
        raise HTTPException(status_code=400, detail="Invalid Admin Token.")
    
    user = crud.user.get(db, model_id=user_id)
    user.is_loggedin = False

    db.add(user) 
    db.commit()
    
    return schemas.UserAccount(
        user=jsonable_encoder(user), 
        account=jsonable_encoder(user.account)
    ) 


@router.get("/2FA/get-2FA-code/", response_model=schemas.TwoFactorAuth)
def get_2FA_code(
    *,
    db: Session = Depends(deps.get_db),
    email_account: str,                           # The email the user signed up with
    email_for_2FA: Optional[str] = None,           # The emal being used for 2FA
    cell_number: Optional[str] = None,            # cell for sms
)-> Any:
    '''
      Generates and sends a 2FA code to the user via sms or email.
    '''      
    def generate_2FA_code() -> str:
        '''
        Generates a 2FA code.
        Code should be 6 Characters letters and numbers
        ex. B5R-922 or XXR-XNR, etc.
        '''  
        characters = string.ascii_uppercase + "0123456789"
        code_2FA = "".join(choice(characters) if pos != 3 else "-"  for pos in range(7)) 
        return code_2FA
     
    code: str = generate_2FA_code()
    tmp_token: str = generate_singleuse_token(email_account, settings.TWO_FACTOR_AUTH_EXPIRE_MINUTES)

    if cell_number is not None:
        message: str = (f"Your {settings.PROJECT_NAME} verification code is: {code} "
                        f"\nThis code will expire in {settings.TWO_FACTOR_AUTH_EXPIRE_MINUTES} minutes. "
                        "Do not share this code with anyone.")
        send_sms(message, cell_number, tmp_token)

    elif email_for_2FA is not None:
        email_obj = schemas.Email(
            email_to="life.package.web@gmail.com", # email_for_2FA
            email_from=settings.EMAIL_FROM,
            subject="Two Factor Authentication Code from Life Package",
            message=build_template_2FA_code(code_2FA=code, email=email_for_2FA),
            user_id=email_account
        )
        send_email(email_obj, tmp_token)

    return schemas.TwoFactorAuth(code=code) #{"code": code} # return the code to da client...


@router.get("/2FA/verify-2FA-code/", response_model=Union[schemas.Token, str])
def verify_2FA_code(
    *,
    db: Session = Depends(deps.get_db),
    current_user:  models.User = Depends(deps.get_current_active_user),
    timed_token: str = Query(...), 
) -> Any:
    '''
    '''    
    if crud.user.is_superuser(current_user):
         user_role ='admin'
    else:
        user_role = 'user'
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


    return {
        "access_token": security.create_access_token(
            current_user.id, 
            user_role, 
            expires_delta=access_token_expires
        ),
        "token_type": "bearer"
    }