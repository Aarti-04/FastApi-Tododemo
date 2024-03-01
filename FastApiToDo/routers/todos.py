import models
from typing import Annotated
from fastapi import Depends, APIRouter,Body, Path,HTTPException,status,Response
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ToDos
from pydantic import BaseModel,Field
from .auth import get_current_user

router=APIRouter()
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
DB_DEPENDENCY=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]
class ToDoRequest(BaseModel):
    title:str=Field(min_length=3)
    description:str=Field(min_length=3,max_length=100)
    priority:int=Field(gt=0,lt=5)
    complete:bool
    class Config:
        json_schema_extra={
            'example':{
                'title':'new task',
                'description':'description',
                'priority':1,
                'complete':False
                }
            }

@router.get("/")
async def read_all(user:user_dependency,db:DB_DEPENDENCY):
    if user is None:
        raise HTTPException(status_code=401,detail="User Is Not Authenticated")
    data=db.query(ToDos).filter(ToDos.owner_id==user.get('id')).all()
    return data
@router.get("/todo/{todo_id}")
async def read_todo(user:user_dependency,db:DB_DEPENDENCY,todo_id:int):
    if user is None:
        raise HTTPException(status_code=401,detail="User Is Not Authenticated")
    todo=db.query(ToDos).filter(ToDos.id==todo_id).filter(ToDos.owner_id==user.get('id')).first()
        # print(todo)
    if todo is not None:
        return todo
    raise HTTPException(status_code=404,detail="Not found")

@router.post("/todo/create_todo")       
async def create_todo(user:user_dependency,db: DB_DEPENDENCY, new_task: ToDoRequest):
    if user is None:
        raise HTTPException(status_code=401,detail="user is not authenticated")
    new_task = ToDos(**new_task.dict(),owner_id=user.get('id'))
    db.add(new_task)
    db.commit()

@router.put("/todo/{todo_id}")
async def update_todo(user:user_dependency,db:DB_DEPENDENCY,todo_id:int,new_updates:ToDoRequest):
    print(todo_id)
    if user is None:
        raise HTTPException(status_code=401,detail="user is not authenticated")
    todo_toupdate=db.query(ToDos).filter(ToDos.id==todo_id).filter(ToDos.owner_id==user.get('id')).first()
    if todo_toupdate is None:
        raise HTTPException(status_code=404,detail="Todo not Found")
    todo_toupdate.title=new_updates.title
    todo_toupdate.description=new_updates.description
    todo_toupdate.priority=new_updates.priority
    todo_toupdate.complete=new_updates.complete
    db.add(todo_toupdate)
    db.commit()
    # return {"created":"create"}
    return todo_toupdate
        
@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:DB_DEPENDENCY,todo_id:int):
    if user is None:
        raise HTTPException(status_code=401,detail="user is not authenticated")
    todo_to_Delete= db.query(ToDos).filter(ToDos.id==todo_id).filter(ToDos.owner_id==user.get("id")).first()
    if todo_to_Delete is None:
        raise HTTPException(status_code=404,detail="Todo not found ")
    db.query(ToDos).filter(ToDos.id==todo_id).filter(ToDos.owner_id==user.get("id")).delete()
    # db.delete(todo_to_Delete)
    db.commit()
    return {"deleted":True}
    