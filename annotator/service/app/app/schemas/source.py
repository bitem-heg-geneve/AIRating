from pydantic import BaseModel, validator


class SourceBase(BaseModel):
    url: str
    text: str | None = None


class SourceCreate(SourceBase):
    "Fields provided by client"
    pass


class Entity(BaseModel):
    label: str
    count: int


class Company(BaseModel):
    label: str
    score: int


class Topic(BaseModel):
    label: str
    score: int


class SourceDetails(SourceBase):
    "Fields returned to client"
    status: str | None = None
    text_token: int | None = None
    text: str | None = None
    impaakt: float | None = None
    entity: list[Entity] | None = None
    company: list[Company] | None = None
    topic: list[Topic] | None = None

    @validator("impaakt")
    def is_check(cls, v):
        if v:
            return round(v, 2)
        else:
            return v
