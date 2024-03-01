import models
from fastapi import FastAPI
from database import engine
import models
from routers import auth,todos,auth1,admin

app=FastAPI(debug=True)

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.router)
# app.include_router(auth1.router)
app.include_router(admin.router)
