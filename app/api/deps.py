from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.database.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    Retrieves the current user based on the provided token.

    Args:
        db (Session): The database session obtained from the `get_db` function.
        token (str): The access token obtained from the client.

    Returns:
        models.User: The retrieved user from the database.

    Raises:
        HTTPException: If the user does not exist, the token is expired, or the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.API_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)

        user = crud.user.get(db, model_id=token_data.sub)
        if not user:
            raise HTTPException(status_code=404, detail="user does not exist")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")

    except (JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="invalid token or credentials")
    


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(
            status_code=401, detail="inactive user"
        )
    
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=401, detail="not superuser"
        )
    
    return current_user

