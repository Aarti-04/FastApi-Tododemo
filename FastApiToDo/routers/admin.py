import models
from typing import Annotated
from fastapi import Depends, APIRouter,Body, Path,HTTPException,status,Response
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ToDos
from pydantic import BaseModel,Field
from .auth import get_current_user

router=APIRouter(
     prefix="/admin",
    tags=['admin']
    )
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
DB_DEPENDENCY=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

@router.get("/")
async def all_todos(user:user_dependency,db:DB_DEPENDENCY):
    if user is None:
        raise HTTPException(status_code=401,detail="User Is Not Authenticated")
    data=db.query(ToDos).all()
    return data
@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:DB_DEPENDENCY,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="user is not authenticated")
    todo_to_Delete= db.query(ToDos).filter(ToDos.id==todo_id).first()
    if todo_to_Delete is None:
        raise HTTPException(status_code=404,detail="Todo not found ")
    db.query(ToDos).filter(ToDos.id==todo_id).delete()
    # db.delete(todo_to_Delete)
    db.commit()
    return {"deleted":True}