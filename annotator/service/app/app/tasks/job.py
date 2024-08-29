import logging
from celery import shared_task
from celery.utils.log import get_logger
from datetime import datetime
from app.models.job import Job

logger = get_logger(__name__)


@shared_task(
    name="ingress:job_start",
    priority=9,
    bind=True,
    default_retry_delay=30,
    max_retries=3,
    soft_time_limit=10000,
)
def job_start(self, job_id):
    job = ~Job.get(job_id)
    job.status = "in progress"
    job.process_start = datetime.now()
    job.save()
    logger.info(f"job_start: {job.id}")
    return job_id


@shared_task(
    name="infer:job_done",
    priority=0,
    bind=True,
    default_retry_delay=30,
    max_retries=3,
    soft_time_limit=10000,
)
def job_done(self, job_id):
    job = ~Job.get(job_id)
    job.process_done = datetime.now()
    job.status = "done"
    job.save()
    logger.info(f"job_done: {job.id}")
    return job_id
