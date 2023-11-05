from datetime import timedelta
from typing import Any

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
    verify_email
)

router = APIRouter()

#
#/api/v1/auth/login/access-token
#
@router.post("/login/access-token", response_model=schemas.Token)
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
    # Expand on this.. Maybe even log all the logins.
    client_host = request.client.host
    logzz.login(f'{client_host}  logged in @: ', timestamp=1)    

    user_role: str

    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Decide if this is a super_user or a normal user and attach it to the response
    if crud.user.is_superuser(user):
         user_role ='admin'
    else:
        user_role = 'user'
        
    # Is this user using 2FA? If so don;t send back the token... send back a mesage to let the client
    # know to invoke the 2FA.
    if user.account.use_2FA: 
        pass
        #return {"msg": "use_2FA"}

    # The client gets the msg to invoke 2FA, the client sends a request to this server @ get-2fa-code/
    # acode is generated and sent to the user either by EMail, SMS. and the client will call the UI
    # component to take the users code input. the code is then sent back to this server @ verify-2fa-code/
    # If theu match then a token is generat3ed, and sent back to the client. 

    return JSONResponse({
        "access_token": security.create_access_token(
            user.id, 
            user_role, 
            expires_delta=access_token_expires
        ),
        "token_type": "bearer"
    })
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


@router.get("/resend-verification/", response_model=schemas.Msg)
def resend_verification(email: EmailStr = Query(...)):
    # Create a new token and send out
    email_token = generate_verifyemail_token(email)
    verify_email(
        email_to='gen.disarray73@outlook.com',  # user_in.email, HARD CODED FOR testing
        email_username=email,
        token=email_token
    )
    logzz.info(f'User: {email} was sent another verify email token.', timestamp=True)
    