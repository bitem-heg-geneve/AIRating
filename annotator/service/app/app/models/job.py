from datetime import datetime
from uuid import UUID, uuid4

from app.models.source import Source
from bunnet import Document, Link
from pydantic import Field
from pydantic import BaseModel
import os


class Job(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    text_token_min: int | None = int(os.environ["TEXT_TOKEN_MIN"])
    text_token_max: int | None = int(os.environ["TEXT_TOKEN_MAX"])
    impaakt_model: bool | None = True
    entity_model: bool | None = True
    company_model: bool | None = True
    topic_model: bool | None = True
    status: str | None = "pending"
    job_created: datetime | None = datetime.now()
    process_start: datetime | None = None
    process_done: datetime | None = None
    process_time: int | None = None
    source: list[Link[Source]]
