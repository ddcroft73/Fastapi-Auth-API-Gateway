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
    
    # This method is used to save obly User data. This should not ever be used but I am leaving it 
    # here for now.
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            phone_number=obj_in.phone_number,
            is_verified=obj_in.is_verified, 
            user_uuid=obj_in.user_uuid,
            cell_provider=obj_in.cell_provider,
            is_loggedin=obj_in.is_loggedin
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    # This method will allow me to get the user.id data back without commiting the data
    # This will ensure that I never have a User without an account.
    def create_no_commit(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            phone_number=obj_in.phone_number,
            is_verified=obj_in.is_verified,
            user_uuid=obj_in.user_uuid,
            cell_provider=obj_in.cell_provider,
            is_loggedin=obj_in.is_loggedin
        )
        db.add(db_obj)
        db.flush()  # add the user but do not commit so I can get back the user.id

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
    
    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser
    
    def user_is_verified(self, user: User) -> bool:
        return user.is_verified
    
    def user_phone_number(self, user: User) -> str:
        return user.phone_number
    
    def is_account_locked(self, user: User) -> bool:
        return user.account_locked
    
    
user = CRUDUser(User)