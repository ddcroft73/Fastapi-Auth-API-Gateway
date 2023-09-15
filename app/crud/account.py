# This class will inherit from base.py and have specific methods for handling the info in the 
#  account table

# Again I'll be using ./user.py as a guide
from typing import Optional, List, Union, Dict, Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.account import Account
#from app.models.user import User
from app.schemas import AccountCreate, AccountUpdate

from app.core.security import get_password_hash, verify_password
from app.utils.api_logger import logzz


class CRUDAccount(CRUDBase[Account, AccountCreate, AccountUpdate]):
    
    def get_by_admin_id(self, db: Session, *, user_id: int) -> Optional[Account]:
        return db.query(Account).filter(Account.id == user_id).first()
        
    def create(self, db: Session, *, obj_in: AccountCreate) -> Account:
        db_obj = Account(
            account_creation_date=obj_in.account_creation_date,
            hashed_admin_PIN=get_password_hash(obj_in.admin_PIN),
            account_last_update_date=obj_in.account_last_update_date,
            last_account_changes_date=obj_in.last_account_changes_date,
            subscription_type=obj_in.subscription_type, 
            last_login_date=obj_in.last_login_date, 
            bill_renew_date=obj_in.bill_renew_date, 
            auto_renewal=obj_in.auto_renewal, 
            account_status_reason=obj_in.account_status_reason,
            cancellation_date=obj_in.cancellation_date,
            cancellation_reason=obj_in.cancellation_reason,
            preferred_contact_method=obj_in.preferred_contact_method,
            timezone=obj_in.timezone
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Account, obj_in: Union[AccountUpdate, Dict[str, Any]]
    ) -> Account:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # updating the PIN, make sure its not saved until its hashed.
        # Its still a password afterall.
        if "admin_PIN" in update_data: 
            hashed_admin_PIN = get_password_hash(update_data["admin_PIN"])
            del update_data["admin_PIN"]
            update_data["hashed_admin_PIN"] = hashed_admin_PIN
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def check_PIN(self, db: Session, *, pin: str, user_id: int) -> Optional[Account]:
        admin = self.get_by_admin_id(db, user_id)
        if not admin:
            return None
        if not verify_password(pin, admin.hashed_admin_PIN):
            return None
        return admin


    # What else do I need to access?
account = CRUDAccount(Account)