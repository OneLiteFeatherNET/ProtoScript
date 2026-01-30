import os
from django.conf import settings

def get_stt_engine():
    engine_type = getattr(settings, 'STT_ENGINE', 'whisper').lower()
    model_name = getattr(settings, 'STT_MODEL', 'openai/whisper-tiny')
    
    if engine_type == 'whisper':
        from .whisper import WhisperEngine
        return WhisperEngine(model_name=model_name)
    elif engine_type == 'mock':
        from .mock import MockEngine
        return MockEngine()
    else:
        raise ValueError(f"Unknown STT Engine: {engine_type}")
