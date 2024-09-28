import sys
sys.stdout.flush()

from fastapi import FastAPI
# from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from .user_routers import admins,users,auth,data_operators,security


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(users.router)
app.include_router(data_operators.router)
app.include_router(security.router)