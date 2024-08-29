from datetime import datetime
from typing import Dict
from uuid import UUID

from app.schemas.source import SourceCreate, SourceDetails
from pydantic import BaseModel, Field, root_validator
from bunnet import PydanticObjectId
import os


class JobBase(BaseModel):
    """Shared fields"""


class JobCreate(JobBase):
    """Fields provided by client"""

    text_token_min: int | None = int(os.environ["TEXT_TOKEN_MIN"])
    text_token_max: int | None = int(os.environ["TEXT_TOKEN_MAX"])
    impaakt_model: bool | None = True
    entity_model: bool | None = True
    company_model: bool | None = True
    topic_model: bool | None = True

    source: list[SourceCreate] = Field(
        example=[
            SourceCreate(
                url="https://www.occ.gov/news-issuances/news-releases/2011/nr-occ-2011-47c.pdf"
            ),
            SourceCreate(
                url="https://www.pionline.com/esg/dws-sell-excessive-greenwashing-doubt-citi-analysts-say"
            ),
            SourceCreate(url="https://www.cnn.com/markets/fear-and-greed"),
            SourceCreate(
                url="https://time.com/personal-finance/article/how-many-stocks-should-i-own/"
            ),
            SourceCreate(
                url="https://wallethub.com/answers/cc/citibank-credit-balance-refund-2140740558/"
            ),
            SourceCreate(
                url="https://www.cnn.com/2021/02/16/business/citibank-revlon-lawsuit-ruling/index.html"
            ),
            SourceCreate(
                url="https://www.businessinsider.com/citi-analysts-excessive-corporate-leverage-2018-11/"
            ),
            SourceCreate(url="https://en.wikipedia.org/wiki/Citibank"),
            SourceCreate(
                url="https://www.propublica.org/article/citi-execs-deeply-sorry-but-dont-blame-us2"
            ),
            SourceCreate(
                url="https://www.cnbc.com/2023/01/11/citi-names-two-asset-classes-to-deploy-excess-cash-for-higher-returns-.html"
            ),
            SourceCreate(
                url="https://www.mckinsey.com/industries/financial-services/our-insights/global-banking-annual-review"
            ),
        ],
        default=[],
    )


class JobCreateStatus(JobBase):
    "Fields returned to client after creating a new Job" ""

    id: UUID = Field(alias="_id")
    text_token_min: int
    text_token_max: int
    impaakt_model: bool
    entity_model: bool
    company_model: bool
    topic_model: bool
    status: str | None
    job_created: datetime


class JobStatus(JobCreateStatus):
    """Status fields returned to client"""

    process_start: datetime | None = None
    process_done: datetime | None = None
    process_time: int | None = None

    @root_validator
    def compute_process_time(cls, values) -> Dict:
        process_start = values.get("process_start")
        process_done = values.get("process_done")
        process_status = values.get("process_status")

        if process_status == "failed":
            values["process_time"] = None

        elif process_start:
            if process_done:
                values["process_time"] = round(
                    (process_done - process_start).total_seconds(), 2
                )
            else:
                values["process_time"] = round(
                    (datetime.now() - process_start).total_seconds(), 2
                )
        else:
            values["process_time"] = None
        return values


class JobDetails(JobStatus):
    """Detail fields returned to client"""

    source: list[SourceDetails]
