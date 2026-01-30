from abc import ABC, abstractmethod

class BaseQueue(ABC):
    @abstractmethod
    def enqueue_protocol_job(self, job_id, template_name):
        """
        Enqueues a protocol processing job.
        """
        pass
