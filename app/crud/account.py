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

class CRUDAccount(CRUDBase[Account, AccountCreate, AccountUpdate]):
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Account]:
        return db.query(Account).filter(Account.user_id == user_id).first()

    def create(self, db: Session, *, obj_in: AccountCreate) -> Account:
        db_obj = Account(  # what about id?
            user_id=obj_in.user_id,
            creation_date=obj_in.creation_date,
            hashed_admin_PIN=get_password_hash(
                obj_in.admin_PIN) if obj_in.admin_PIN else None,
            last_update_date=obj_in.last_update_date,
            subscription_type=obj_in.subscription_type, 
            last_login_date=obj_in.last_login_date, 
            bill_renew_date=obj_in.bill_renew_date, 
            auto_bill_renewal=obj_in.auto_bill_renewal,
            account_locked=obj_in.account_locked,  
            account_locked_reason=obj_in.account_locked_reason,
            cancellation_date=obj_in.cancellation_date,
            cancellation_reason=obj_in.cancellation_reason,
            preferred_contact_method=obj_in.preferred_contact_method,
            timezone=obj_in.timezone,

            use_2FA=obj_in.use_2FA,
            contact_method_2FA=obj_in.contact_method_2FA,
            cell_provider_2FA=obj_in.cell_provider_2FA,
            last_logout_date=obj_in.last_logout_date
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def create_no_commit(self, db: Session, *, obj_in: AccountCreate) -> Account:
        db_obj = Account(  # what about id?
            user_id=obj_in.user_id,
            creation_date=obj_in.creation_date,
            hashed_admin_PIN=get_password_hash(
                obj_in.admin_PIN) if obj_in.admin_PIN else None,
            last_update_date=obj_in.last_update_date,
            subscription_type=obj_in.subscription_type,
            last_login_date=obj_in.last_login_date,
            bill_renew_date=obj_in.bill_renew_date,
            auto_bill_renewal=obj_in.auto_bill_renewal,
            account_locked=obj_in.account_locked,
            account_locked_reason=obj_in.account_locked_reason,
            cancellation_date=obj_in.cancellation_date,
            cancellation_reason=obj_in.cancellation_reason,
            preferred_contact_method=obj_in.preferred_contact_method,
            timezone=obj_in.timezone,
            
            use_2FA=obj_in.use_2FA,
            contact_method_2FA=obj_in.contact_method_2FA,
            cell_provider_2FA=obj_in.cell_provider_2FA,
            last_logout_date=obj_in.last_logout_date
        )
        db.add(db_obj)
        db.flush()
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
        account = self.get_by_user_id(db, user_id)

        if not account:
            return None
        if not verify_password(pin, account.hashed_admin_PIN):
            return None
        return account

account = CRUDAccount(Account)