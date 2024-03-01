from datetime import timedelta,datetime
from typing import Annotated
from fastapi import APIRouter, Depends,status,HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
router=APIRouter(
    prefix="/auth",
    tags=['auth']
    )

SECRET_KEY="2f66619911820a0930a4991fa4e06d00fcc94c542acdfb8f206ca950c2f18c0b"
ALGORITHM="HS256"
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
outh2_bearer=OAuth2PasswordBearer(tokenUrl="auth/token")
class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    is_active:bool
    role:str
class token(BaseModel):
    access_token:str
    token_type:str
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
DB_DEPENDENCY=Annotated[Session,Depends(get_db)]
def authenticate(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user
def create_access_token(username:str,user_id:int,role:str,expires_delta:timedelta):
    encode={'sub':username,'id':user_id,'role':role}
    expires=datetime.utcnow() +expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)
async def get_current_user(token:Annotated[str,Depends(outh2_bearer)]):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username:str=payload.get('sub')
        userid:int=payload.get('id')
        role:str=payload.get('role')
        if username is None or userid is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate with credentials")
        return {"username":username,"id":userid,"role":role}
    except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate with credentials")

@router.post("/",status_code=status.HTTP_201_CREATED)
def create_user(db:DB_DEPENDENCY,create_user_request:CreateUserRequest):
    # user= Users(**create_user_request.dict())
    user=Users(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        is_active=create_user_request.is_active,
        role=create_user_request.role
        )
    db.add(user)
    db.commit()
    return user
@router.post("/token",response_model=token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:DB_DEPENDENCY):
    user= authenticate(form_data.username,form_data.password,db)
    print(user)
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate to user")
    token=create_access_token(user.username,user.id,user.role,timedelta(minutes=20))
    return {"access_token":token,"token_type":'Bearer'}