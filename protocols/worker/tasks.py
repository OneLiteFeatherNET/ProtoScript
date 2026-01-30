import os
import tempfile
import json
from celery import shared_task
from django.utils import timezone
from protocols.core.s3_storage import S3Storage
from protocols.core.utils import transcribe_audio, generate_protocol

@shared_task
def process_protocol_task(job_id, template_name='default.md.j2'):
    storage = S3Storage()
    storage.update_status(job_id, {'status': 'processing', 'started_at': timezone.now().isoformat()})

    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as tmpdir:
            # Download meta and audio from S3
            meta_path = os.path.join(tmpdir, 'meta.json')
            audio_path = os.path.join(tmpdir, 'audio.flac')
            
            storage.download_file(f"jobs/{job_id}/meta.json", meta_path)
            storage.download_file(f"jobs/{job_id}/audio.flac", audio_path)
            
            with open(meta_path, 'r') as f:
                meta_data = json.load(f)

            # Transcribe
            transcriptions = transcribe_audio(audio_path, meta_data.get('users', {}))

            # Load template (we still keep templates locally in the monolith for now, 
            # as they are part of the "Prod Code")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(base_dir, 'templates', 'protocols', os.path.basename(template_name))
            
            if not os.path.exists(template_path):
                 template_path = os.path.join(base_dir, 'templates', 'protocols', 'default.md.j2')
            
            with open(template_path, 'r') as f:
                template_content = f.read()

            # Generate protocol
            protocol = generate_protocol(meta_data, transcriptions, template_content)

            # Save result to S3
            storage.save_result(job_id, protocol)
            storage.update_status(job_id, {
                'status': 'completed', 
                'completed_at': timezone.now().isoformat()
            })

    except Exception as e:
        storage.update_status(job_id, {
            'status': 'failed',
            'error_message': str(e)
        })
        raise e
