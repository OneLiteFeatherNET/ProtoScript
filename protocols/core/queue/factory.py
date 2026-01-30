import os
from django.conf import settings
from .celery_queue import CeleryQueue

def get_queue_backend():
    backend_type = getattr(settings, 'QUEUE_BACKEND', 'celery').lower()
    
    if backend_type == 'celery':
        return CeleryQueue()
    else:
        # Fallback to Celery
        return CeleryQueue()
