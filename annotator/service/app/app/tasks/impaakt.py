import logging
import os
import pickle

from app.models.job import Job
from app.models.source import Source
from celery import shared_task
from celery.utils.log import get_logger

MODEL_FP = r"/resources/impaakt/impaakt.pckl"


@shared_task(
    name="infer:source_impaakt",
    bind=True,
    default_retry_delay=30,
    max_retries=3,
    soft_time_limit=10000,
)
def source_impaakt(self, job_id, source_ids):
    try:
        # load job
        job = ~Job.get(job_id)
        if job.status == "failed":
            return job_id

        # load sources
        sources = [~Source.get(sid) for sid in source_ids]
        sources = [s for s in sources if s.status != "failed"]

        # load model
        model = pickle.load(open(MODEL_FP, "rb"))

        # run model
        impaakt_probas = model.predict_proba([s.text for s in sources])

        # update sources
        for source, ip in zip(sources, impaakt_probas):
            # probas = model.predict_proba([source.text])
            source.impaakt = ip[1] * 100.0
            source.save()

    except Exception as e:
        job.status = "failed"
        job.save()
        logging.info(f"job {job.id}: failed")

    return job_id
