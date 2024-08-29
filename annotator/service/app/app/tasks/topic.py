import csv
import json
import logging
import os
import pickle
from dataclasses import dataclass
from difflib import SequenceMatcher

import numpy as np
import pandas as pd
import torch
from celery import shared_task
from app.models.job import Job
from app.models.source import Source, Topic

MODEL_FP = r"/resources/topics/model_alltopics_dumpv1_oct14"
TOPICS_FP = r"/resources/topics/impaakt_topics_march23.csv"


@shared_task(
    name="infer:job_topic",
    bind=True,
    default_retry_delay=30,
    max_retries=3,
    soft_time_limit=10000,
)
def source_topic(self, job_id, source_ids):
    try:
        # load job
        job = ~Job.get(job_id)
        if job.status == "failed":
            return job_id

        # load sources
        sources = [~Source.get(sid) for sid in source_ids]
        sources = [s for s in sources if s.status != "failed"]

        # load model
        input_file_topics = csv.DictReader(open(TOPICS_FP))
        mapping_topics = {row["id"]: row["name"] for row in input_file_topics}
        
        model = pickle.load(open(MODEL_FP, "rb"))
        tmodel = model["topic_classifier"]
        tfidf = model["content_vector"]
        ldv = model["topics"]
        
        # Create a list of class names from the mapping
        class_names = [mapping_topics[cname] for cname in tmodel.classes_]
        
        # Run model
        texts = tfidf.transform(np.array([s.text for s in sources]))
        lda = ldv.transform(texts)
         
        # Get the probability distribution for each source in the batch
        topics_proba_batch = tmodel.predict_proba(lda)
        
        
        # class_names = []
        # for cname in tmodel.classes_:
        #     class_names.append(mapping_topics[cname])

        # run model
        texts = tfidf.transform(np.array([s.text for s in sources]))
        lda = ldv.transform(texts)
        topics_proba = dict(zip(class_names, tmodel.predict_proba(lda)))
        topics_proba_batch = tmodel.predict_proba(lda)
        
        # Update sources with their corresponding topics and scores
        for source, topic_proba in zip(sources, topics_proba_batch):
            source.topic = [
                Topic(label=label, score=score * 100.0)
                for label, score in zip(class_names, topic_proba)
            ]
            source.save()
        
        return job_id

    except Exception as e:
        # Handle the exception and log the error
        job = Job.get(job_id)
        job.status = "failed"
        job.save()
        logging.error(f"Job {job_id} failed: {e}")
        return job_id    
            
        
