from typing import Optional, List, Union, Dict, Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas import UserCreate, UserUpdate

from app.core.security import get_password_hash, verify_password
from app.utils.api_logger import logzz

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # Declare model specific CRUD operation methods.
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            # New 
            phone_number=obj_in.phone_number, #if obj_in.phone_number else None,
            is_verified=obj_in.is_verified, # if obj_in.is_verified else False,
            failed_attempts=obj_in.failed_attempts, # if obj_in.failed_attempts else 0,
            account_locked=obj_in.account_locked, # if obj_in.account_locked else False  
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if "password" in update_data: #if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
## TODO:
## Add methods to retrieve:
# phone_number
# is_verified: 
# failed_attempts
# account_locked

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

user = CRUDUser(User)