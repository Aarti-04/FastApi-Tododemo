from database import Base
from sqlalchemy import func,Column,Integer,String,Boolean,DateTime,ForeignKey

class Users(Base):
    __tablename__="users"

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String(50),unique=True)
    username=Column(String(20),unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password=Column(String)
    is_active=Column(Boolean,default=True)
    role=Column(String)



class ToDos(Base):
    __tablename__="todos"
        # sno=Column(Integer,primary_key=True)
        # title=Column(String(50),nullable =True)
        # description=Column(String(300),nullable=True)
        # priority=Column(Integer)
        # complete=Column(Boolean)
        # created_at=Column(DateTime,default=func.now())
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(50),nullable =True)
    description=Column(String(300),nullable=True)
    priority=Column(Integer)
    complete=Column(Boolean,default=False)
    owner_id=Column(Integer,ForeignKey("users.id"))