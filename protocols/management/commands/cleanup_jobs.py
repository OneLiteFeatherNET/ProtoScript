from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from protocols.core.s3_storage import S3Storage

class Command(BaseCommand):
    help = 'Deletes old protocol jobs from S3.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=60,
            help='Delete jobs older than this many minutes (default: 60)'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        threshold = timezone.now() - timedelta(minutes=minutes)
        storage = S3Storage()
        
        job_ids = storage.list_job_ids()
        count = 0
        
        for job_id in job_ids:
            status = storage.get_status(job_id)
            if not status:
                # If no status file, maybe it's broken or partially uploaded, delete it?
                # For safety, let's only delete if it's really old based on S3 metadata?
                # Actually, let's just skip it if we can't determine age.
                continue
            
            created_at_str = status.get('created_at')
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
                # Ensure it's timezone aware for comparison if needed
                if created_at.tzinfo is None:
                    from django.utils.timezone import make_aware
                    created_at = make_aware(created_at)
                
                if created_at < threshold:
                    storage.delete_job(job_id)
                    count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old jobs from S3.'))
