import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.telegram_routes import router as telegram_router
from app.auth_routes import router as auth_router

app = FastAPI()

PORT = os.getenv("FRONTEND_PORT", "3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telegram_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}
