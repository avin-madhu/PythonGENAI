from sqlalchemy import Integer, Column, Boolean, String

from todoBackend.database import Base


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    completed = Column(Boolean)
