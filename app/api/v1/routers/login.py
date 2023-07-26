from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse


router = APIRouter()

# Password recovery, Login, signup

@router.post("/login/access-token")#, response_model=schemas.Token)
def login_access_token():
    pass

@router.post("/login/test-token")#, response_model=schemas.User)
def test_token():
    pass

@router.post("/password-recovery/{email}")#, response_model=schemas.Msg)
def recover_password():
    pass

@router.post("/reset-password/")#, response_model=schemas.Msg)
def reset_password():
    pass

