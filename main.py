from fastapi import FastAPI
from app.api import facebook_creatives
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Facebook Creatives API")

origins = [
    "http://localhost:5173",
    "https://creatives-ui-9f021aba052c.herokuapp.com",
    "https://creatives-ui-9f021aba052c.herokuapp.com/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(facebook_creatives.router, prefix="/api")
