from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Path
from models import Users
from database import SessionLocal
from pydantic import BaseModel, Field
from starlette import status
from helpers import get_db
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

# user details
@router.get("/user-details/{user_id}", status_code=status.HTTP_200_OK)
async def user_details(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Users).filter(Users.id == user_id).first()

# change password
@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    