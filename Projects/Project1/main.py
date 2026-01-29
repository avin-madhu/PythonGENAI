from fastapi import FastAPI

from Project1.api.v1 import health, auth
from Project1.config import settings
from Project1.db.initDB import init_db
from Project1.db.session import engine

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def on_startup():
    await init_db(engine)


app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
