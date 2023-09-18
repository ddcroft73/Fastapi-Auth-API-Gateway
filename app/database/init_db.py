from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.core.config import settings
from app.utils.api_logger import logzz
from app.database import base  
from datetime import datetime

def init_db(db: Session) -> None:

    #current_date: datetime = datetime.today()
    #formatted_date_today: str = current_date.strftime('%m/%d/%Y')

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,  
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Danny the ADMIN",            
            is_superuser=True
        )

    try:
        # This method only adds and flushes, does not commit, Should never neeed to add User data solo
        # however crud.user.create() does just that.
        user: models.User = crud.user.create_rollback(db, obj_in=user_in)    

        # Account fields can be totally default except for user_id, 
        # I need that to tie it to its respected user.
        account_in = schemas.AccountCreate(
            user_id=user.id,
            admin_PIN="112233", # Change this if keeping this account
            timezone='Eastern'
        )               
        account: models.Account = crud.account.create_rollback(db, obj_in=account_in)
        
        db.commit()
        db.refresh(user)
        db.refresh(account)

    except Exception as exc:
         logzz.error(str(exc))
         db.rollback() 
