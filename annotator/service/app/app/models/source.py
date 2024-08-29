from bunnet import Document
from pydantic import BaseModel
from typing import Optional


class Entity(BaseModel):
    label: str
    count: int


class Company(BaseModel):
    label: str
    score: int


class Topic(BaseModel):
    label: str
    score: int


class Source(Document):
    url: str
    status: str | None = None
    text: str | None = None
    text_token: int | None = None
    impaakt: float | None = None
    entity: Optional[list[Entity]]
    company: Optional[list[Company]]
    topic: Optional[list[Topic]]
