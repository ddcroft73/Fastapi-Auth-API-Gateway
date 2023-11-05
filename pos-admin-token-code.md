If your current system already has a complex validation mechanism that you don't want to disturb, and you're looking to include the `admin_token` within the payload while keeping the update data structured as you've indicated, then you can slightly modify the endpoint to extract the `admin_token` from the incoming payload.

Here's how you can modify your endpoint to accommodate the `admin_token` within the structured payload:

```python
from pydantic import BaseModel, Field

# Define a new Pydantic model that includes the admin_token alongside the update models
class UpdateData(BaseModel):
    user_in: schemas.UserUpdate
    account_in: schemas.AccountUpdate
    admin_token: str = Field(..., description="Admin token for an additional security layer")

@router.put("/update/{user_id}", response_model=schemas.UserAccount)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    update_data: UpdateData,  # Use the new Pydantic model
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user. SuperUser action. 
    """
    # Extract the admin_token from the update data
    admin_token = update_data.admin_token
    if not validate_admin_token(admin_token):  # Your existing validation logic
        raise HTTPException(status_code=403, detail="Admin token invalid")

    user = crud.user.get(db, model_id=user_id)
    account = current_user.account

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    # Update the user and account with the provided update data
    user = crud.user.update(db, db_obj=user, obj_in=update_data.user_in)
    account = crud.account.update(db, db_obj=account, obj_in=update_data.account_in)

    return schemas.UserAccount(user=user, account=account)
```

In this setup, your `UpdateData` model encapsulates all the update information and the `admin_token`. This model is then used as the expected body of the PUT request. The endpoint function extracts the `admin_token` from the `UpdateData` model and passes the rest of the update information to the respective CRUD operations.

This way, you can easily extract and validate the `admin_token` without restructuring your existing token validation system. The actual validation function `validate_admin_token` should be one you have defined elsewhere, which checks the validity of the provided admin token.