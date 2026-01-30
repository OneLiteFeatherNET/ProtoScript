import jinja2
import soundfile as sf
import os
from datetime import datetime, timedelta
from django.utils import timezone
from .engines.factory import get_stt_engine

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = get_stt_engine()
    return _engine

def transcribe_audio(audio_file_path, users):
    # Read audio with soundfile
    data, samplerate = sf.read(audio_file_path)
    
    engine = get_engine()
    return engine.transcribe(data, samplerate, users)

def generate_protocol(meta_data, transcriptions, template_content):
    # Parse date formats
    def parse_dt(dt_str):
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            # If the format is slightly different
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")

    start_time = parse_dt(meta_data['start_time'])
    end_time = parse_dt(meta_data['end_time'])
    
    timeline = []
    
    # Add events
    for event in meta_data.get('events', []):
        timeline.append({
            'type': 'event',
            'timestamp': parse_dt(event['timestamp']),
            'content': event['message']
        })
    
    # Add transcriptions
    for t in transcriptions:
        abs_ts = start_time + timedelta(seconds=t['timestamp'])
        timeline.append({
            'type': 'transcript',
            'timestamp': abs_ts,
            'user_id': t['user_id'],
            'user_name': t['user_name'],
            'text': t['text']
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x['timestamp'])
    
    # Render template
    env = jinja2.Environment()
    template = env.from_string(template_content)
    
    # Prepare meta data
    meta_for_template = meta_data.copy()
    meta_for_template['start_time'] = start_time
    meta_for_template['end_time'] = end_time
    
    # Insert User IDs into the user object
    for uid, uinfo in meta_for_template['users'].items():
        uinfo['id'] = uid

    return template.render(meta=meta_for_template, timeline=timeline)

