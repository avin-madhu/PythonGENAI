from typing import Optional

from fastapi import FastAPI

app = FastAPI()

db = [
    "batman",
    "superman",
    "wonder woman",
    "martian manhunter",
    "flash",
    "cyborg"
]


# main getter method
@app.get("/items/users")
async def read_users(username: str):
    return [{"name": "avin"}, {"name": username}]


# file path catchers
@app.get("/files/{filepath:path}")
async def read_files(filepath: str | None = None):
    data = await read_users("athul")
    return data


# get using queries
@app.get("/dc/")
async def get_heroes(start: int = 0, end: Optional[int] = None):
    return db[start:end]
