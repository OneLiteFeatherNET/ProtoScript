from .base import STTEngine

class MockEngine(STTEngine):
    def transcribe_channel(self, channel_data, samplerate):
        return [{
            'type': 'transcript',
            'timestamp': 1.0,
            'text': 'This is a mock transcription.'
        }]
