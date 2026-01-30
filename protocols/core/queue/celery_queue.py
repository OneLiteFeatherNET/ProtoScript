from .base import BaseQueue
from protocols.worker.tasks import process_protocol_task

class CeleryQueue(BaseQueue):
    def enqueue_protocol_job(self, job_id, template_name):
        process_protocol_task.delay(job_id, template_name=template_name)
