from fastapi import APIRouter,Depends,status,HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt
from datetime import timedelta,datetime
router=APIRouter(
    prefix="/auth1",
    tags=['auth1'])
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated="auto")
class UserRequest(BaseModel):
    username:str
    email:str
    password:str
    first_name:str
    last_name:str
    is_active:bool
    role:str

class Token(BaseModel):
    access_key:str
    key_type:str
DB_DEPENDENCY=Annotated[Session,Depends(get_db)]
SECERET_KEY="75e0c8161e29f1ab44ca6aa0abc5ac7cafa07ef435b25fa62e5b997536cb11d4"
ALGORITHM="HS256"
@router.get("/users")
async def get_user():
    return "hello"
@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:DB_DEPENDENCY,create_user_request:UserRequest):
    user=Users(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        is_active=create_user_request.is_active
        )
    db.add(user)
    db.commit()
def authenticate(username:str,password:str,db):
    user= db.query(Users).filter(Users.username==username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user
def create_auth_token(username:str,userid:int,expires_time:timedelta):
    
    encode={"sub":username,"id":userid}
    expire_time=datetime.utcnow()+expires_time
    encode.update({"exp":expire_time})
    return jwt.encode(encode,SECERET_KEY,algorithm=ALGORITHM)

@router.post("/token",response_model=Token)
async def create_access_token(user_request:Annotated[OAuth2PasswordRequestForm,Depends()],db:DB_DEPENDENCY):
    user=authenticate(user_request.username,user_request.password,db)
    token=create_auth_token(user.username,user.id,timedelta(minutes=20))
    return {"access_key":token,"key_type":"Bearer"}
