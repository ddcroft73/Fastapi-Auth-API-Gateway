from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.database import base  

def init_db(db: Session) -> None:
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Danny D.C.",            
            is_superuser=True
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841