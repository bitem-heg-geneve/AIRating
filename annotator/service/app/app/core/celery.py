from celery import current_app as current_celery_app

from app.core.config import settings


def create_celery():
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")
    celery_app.conf.broker_transport_options = {
        'priority_steps': list(range(10)),
        "queue_order_strategy": "priority",
    }

    return celery_app
