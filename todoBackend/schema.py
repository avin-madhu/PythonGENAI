from pydantic import BaseModel


class TodoSchema(BaseModel):
    id: int
    text: str
    completed: bool
