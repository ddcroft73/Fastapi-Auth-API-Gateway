from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.core.config import settings
from app.utils.api_logger import logzz

def init_db(db: Session) -> None:

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,  
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Work damn ya!",            
            is_superuser=True
        )

    try:
        user: models.User = crud.user.create_no_commit(db, obj_in=user_in)

        # Account fields can be totally default except for user_id, 
        # I need that to tie it to its respected user.
        account_in = schemas.AccountCreate(
            user_id=user.id,
            admin_PIN="112233", # Change this if keeping this account
            timezone='Eastern'
        )               
        account: models.Account = crud.account.create_no_commit(db, obj_in=account_in)
        
        db.commit()
        db.refresh(user)
        db.refresh(account)

    except Exception as exc:
         logzz.error(str(exc))
         db.rollback()   # utilize Atomic transaction. Cant have a user without account and vice versa.
