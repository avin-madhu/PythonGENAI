from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from todoBackend import models
from todoBackend import schema
from todoBackend.database import engine, SessionLocal
from todoBackend.models import Base

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# makes all the tables in the database on run
Base.metadata.create_all(bind=engine)


# dependency to get a DB connection
async def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# get method
@app.get("/tasks", response_model=list[schema.TodoSchema])
async def get_tasks(db: Session = Depends(get_db_session)):
    data = db.query(models.Todo).all()
    return data


@app.post("/task", response_model=schema.TodoSchema)
async def post_task(todo: schema.TodoSchema
                    , db: Session = Depends(get_db_session)):
    data = models.Todo(**todo.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@app.patch("/edit/{id}", response_model=schema.TodoSchema)
async def edit_task(id: int, todo: schema.TodoSchema, db: Session = Depends(get_db_session)):
    query = db.query(models.Todo).filter(models.Todo.id == id)
    data = query.first()
    update_data = todo.dict(exclude_unset=True)
    query.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(data)

    return data


@app.delete("/delete/{id}", response_model=schema.TodoSchema)
async def delete_task(id: int, todo: schema.TodoSchema, db: Session = Depends(get_db_session)):
    query = db.query(models.Todo).filter(models.Todo.id == id)
    data = query.first()

    query.delete(synchronize_session=False)
    db.commit()
    db.refresh(data)

    return data
