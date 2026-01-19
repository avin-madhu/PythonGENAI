from fastapi import FastAPI

from project1.api.v1 import health, auth
from project1.config import settings
from project1.db.initDB import init_db
from project1.db.session import engine

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def on_startup():
    await init_db(engine)


app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
