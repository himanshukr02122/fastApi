from datetime import timedelta, datetime, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from helpers import get_db
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY="f484923ccdfab4de33acd17c0f4866f38b22da396bcd776cc1a32deb149c805c"
ALGORITHM="HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):

    encode = { 'sub': username, "id": user_id, "role": role }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate User")
        return {
            "username": username,
            "id": user_id,
            "user_role": user_role
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate User")


class Create_User_Request(BaseModel):
    
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_request_body: Create_User_Request):
    
    create_user_model = Users(
        email= create_request_body.email,
        username= create_request_body.username,
        first_name= create_request_body.first_name,
        last_name= create_request_body.last_name,
        hashed_password= bcrypt_context.hash(create_request_body.password),
        role= create_request_body.role,
        is_active= True
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model

@router.get("/users")
async def get_all_users(db: db_dependency):
    return db.query(Users).all()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate User")
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {
        "access_token": token,
        "token_type": "bearer"
    }