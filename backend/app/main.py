from fastapi import FastAPI
from app.telegram_routes import router as telegram_router
from app.auth_routes import router as auth_router

app = FastAPI()
app.include_router(telegram_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}
