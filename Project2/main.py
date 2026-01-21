import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.database import engine, Base
from api.routes import auth, tools, reviews, count
from seed import DatabaseSeeder

seeder = DatabaseSeeder()


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seeder.seed_data()

    yield
    await engine.dispose()


app = FastAPI(
    title="AI Tool Finder API",
    lifespan=lifespan,
)

# Middleware and Routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tools.router)
app.include_router(reviews.router)
app.include_router(count.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8001,
        reload=True,
    )