from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Path
from models import Todos
from database import SessionLocal
from pydantic import BaseModel, Field
from starlette import status
from helpers import get_db
from .auth import get_current_user

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class Request_Body(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

@router.get("/",  status_code=status.HTTP_200_OK)
async def get_all_todo_list(db: db_dependency):
    return db.query(Todos).all()

# get all todos by user_id

@router.get("/get_all_todos_by_user", status_code=status.HTTP_200_OK)
async def get_all_todos_by_user(user: user_dependency, db: db_dependency):
    if user is None:
     raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/get_todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: int=Path(gt=0)):
    if user is None:
     raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
       return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.") 


# create todo

@router.post("/todo/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, request_body: Request_Body):

    if user is None:
     raise HTTPException(status_code=401, detail="Authentication failed")
    print(request_body, "request_body")
    todo_model = Todos(**request_body.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()

# update todo

@router.put("/todo/update_todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, request_body: Request_Body, id: int = Path(gt=0)):
    if user is None:
     raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    todo_model.title = request_body.title
    todo_model.description = request_body.description
    todo_model.priority = request_body.priority
    todo_model.complete = request_body.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
     raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    db.query(Todos).filter(Todos.id == id).delete()

    db.commit()