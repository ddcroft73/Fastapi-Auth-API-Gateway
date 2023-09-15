from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.database import base  
from datetime import datetime

def init_db(db: Session) -> None:

    current_date: datetime = datetime.today()
    formatted_date_today: str = current_date.strftime('%m/%d/%Y')
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Danny D.C.",            
            is_superuser=True
        )
        account_in = schemas.AccountCreate(
            account_creation_date=formatted_date_today,
            last_login_date=formatted_date_today,
            bill_renew_date=formatted_date_today,
            last_account_changes_date=formatted_date_today,
            account_last_update_date=formatted_date_today,
            admin_PIN="112233", # Change this if keeping this account
            timezone='Eastern'
        )
        user: schemas.User = crud.user.create(db, obj_in=user_in)  # noqa: F841
        account: schemas.Account = crud.account.create(db, obj_in=account_in)
