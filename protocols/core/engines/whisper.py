import torch
from transformers import pipeline
from .base import STTEngine

class WhisperEngine(STTEngine):
    def __init__(self, model_name="openai/whisper-tiny", device=None):
        if device is None:
            device = 0 if torch.cuda.is_available() else -1
        self.asr = pipeline("automatic-speech-recognition", model=model_name, device=device)

    def transcribe_channel(self, channel_data, samplerate):
        channel_transcripts = []
        result = self.asr({"sampling_rate": samplerate, "raw": channel_data}, return_timestamps=True)
        
        chunks = result.get('chunks', [])
        if not chunks and result.get('text'):
            chunks = [{'timestamp': (0.0, None), 'text': result['text']}]
            
        for chunk in chunks:
            if chunk['timestamp'][0] is not None:
                channel_transcripts.append({
                    'type': 'transcript',
                    'timestamp': float(chunk['timestamp'][0]),
                    'text': chunk['text'].strip()
                })
        return channel_transcripts
