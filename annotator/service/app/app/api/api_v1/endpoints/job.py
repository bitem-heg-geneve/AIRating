from typing import Any, Dict

from app.models.job import Job
from app.schemas.job import (
    JobCreate,
    JobCreateStatus,
    JobDetails,
    JobStatus,
)
from app.tasks.job import job_done, job_start
from app.tasks.text import source_text
from app.tasks.impaakt import source_impaakt
from app.tasks.company import source_company
from app.tasks.entity import source_entity
from app.tasks.topic import source_topic
from bunnet import WriteRules
from celery import chain, group
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()


@router.post(
    "",
    status_code=200,
    response_model=JobCreateStatus,
)
def create_job(
    *,
    job_in: JobCreate,
) -> dict:
    # ) -> Any:
    """\
    Create an Impaakt job including a list of candicate sources. 
    1. Each source must include an url \n
    2. For each source a text can optionally be included in the request. For sources for which no text is provided, the system will attempt to crawl the url and extract text from either html or PDF documents. Only source-texts with a number of tokens in excess of min_text_token are eligle for impaakt, entity, company and topic inference.
    \n
    3. Impaakt inference is default but optional. Only sources with text will be processed.
    4. Entity recognition (NER) is optional. For each source a NER-list can be included in the request. For sources for which no NER-list is provided the system will attempt to extract entities. \n Only sources with text will be processed. \n
    5. Company classification is optional. Only sources with a NER-list will be processed.
    6. SASB topic classification is optional. Only sources with a NER-list will be processed.
    
    """
    job = Job(**job_in.dict())
    job = job.insert(link_rule=WriteRules.WRITE)

    n = int(os.environ["SOURCE_BATCH_SIZE"])

    jc = []  # job chain
    jc.append(job_start.si(job.id))

    # parallel processing of source batches
    bg = []  # batch group
    for b in (job.source[i : i + n] for i in range(0, len(job.source), n)):
        # for each source batch; first get text, next run models
        bc = []  # batch chain
        source_ids = [str(s.id) for s in b]
        bc.append(source_text.si(str(job.id), source_ids))
        if job.impaakt_model | job.entity_model | job.company_model | job.entity_model:
            mg = []  # model group
            if job.impaakt_model:
                mg.append(source_impaakt.si(str(job.id), source_ids))

            if job.entity_model | job.company_model:
                cmc = []  # company model chain
                if job.entity_model:
                    cmc.append(source_entity.si(str(job.id), source_ids))

                if job.company_model:
                    cmc.append(source_company.si(str(job.id), source_ids))
                mg.append(chain(cmc))

            if job.topic_model:
                mg.append(source_topic.si(str(job.id), source_ids))

            bc.append(group(mg))
        bg.append(chain(bc))
    jc.append(group(bg))
    jc.append(job_done.si(job.id))

    chain(jc).apply_async()

    return job


@router.get(
    "/{id}/status",
    status_code=200,
    response_model=JobStatus,
    response_model_exclude_none=True,
)
def job_status(
    *,
    id: str,
) -> Any:
    """
    Retrieve job status by job_id.
    """
    try:
        job = ~Job.get(id).project(JobStatus)

    except:
        raise HTTPException(status_code=404, detail=f"Job with ID {id} not found")

    return job


@router.get(
    "/{id}",
    status_code=200,
    response_model=JobDetails,
    response_model_exclude_none=True,
)
def job_details(
    *,
    id: str,
    include_text: bool = False,
    include_entity: bool = False,
) -> Any:
    """
    Retrieve job by ID\n
    Optionally includes text and NER.
    """
    try:
        job = ~Job.get(id, fetch_links=True)
        if not include_text:
            for source in job.source:
                source.text = None

        if not include_entity:
            for source in job.source:
                source.entity = None
    except:
        raise HTTPException(status_code=404, detail=f"Job with ID {id} not found")

    return job
