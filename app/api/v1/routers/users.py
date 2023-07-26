from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse


router = APIRouter()

# Get users, add users, delete users, edit users

@router.get('/')
def root():
    return {'result': "Root Endpoint"}

@router.post("/")#, response_model=schemas.User)
def create_user():
    pass

@router.post('/get-users/', tags=["Users"])
def get_all_users(skip: int = 0, limit: int = 100): #, db: Session = Depends(get_db)):
    return {'result': "get-users"}


@router.post('/get-user/{user_id}', tags=["Users"])
def get_user():
    return {'result': "get-users"}


@router.get("/users/me", tags=['Users']) #,response_model=UserSchema)
def get_users_me():
    return {'result': 'get-users-me'}


@router.delete("/users/{user_id}", tags=['Users'])
def delete_user(user_id: str):
    return {'result': "delete a user {user_id}"}