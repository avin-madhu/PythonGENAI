from pydantic import BaseModel


class QuerySchema(BaseModel):
    id: int
    role: str
    query: str


class QueryResponseSchema(BaseModel):
    id: int
    role: str
    content: str
