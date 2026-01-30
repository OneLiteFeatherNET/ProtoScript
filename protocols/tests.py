from django.test import SimpleTestCase, Client
from django.urls import reverse
import json
import os
from unittest.mock import patch, MagicMock

class ProtocolApiTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.meta_path = os.path.join(self.base_dir, 'tests/assets/meta.json')
        self.audio_path = os.path.join(self.base_dir, 'tests/assets/audio_protocol.flac')

    @patch('protocols.api.views.S3Storage')
    @patch('protocols.api.views.get_queue_backend')
    def test_protocol_request_success(self, mock_get_queue, mock_storage_class):
        mock_storage = mock_storage_class.return_value
        mock_queue = mock_get_queue.return_value
        url = reverse('protocol_request')
        
        with open(self.meta_path, 'rb') as meta_file, open(self.audio_path, 'rb') as audio_file:
            response = self.client.post(url, {
                'meta': meta_file,
                'audio': audio_file
            })
            
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertIn('id', data)
        self.assertEqual(data['status'], 'pending')
        
        # Verify S3 calls
        self.assertTrue(mock_storage.upload_file.called)
        self.assertTrue(mock_storage.update_status.called)
        # Verify Queue call
        self.assertTrue(mock_queue.enqueue_protocol_job.called)

    @patch('protocols.api.views.S3Storage')
    def test_protocol_result_status(self, mock_storage_class):
        mock_storage = mock_storage_class.return_value
        job_id = '550e8400-e29b-41d4-a716-446655440000'
        mock_storage.get_status.return_value = {'id': job_id, 'status': 'processing'}
        
        url = reverse('protocol_result', kwargs={'job_id': job_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'processing')

    @patch('protocols.api.views.S3Storage')
    def test_protocol_result_completed(self, mock_storage_class):
        mock_storage = mock_storage_class.return_value
        job_id = '550e8400-e29b-41d4-a716-446655440000'
        mock_storage.get_status.return_value = {'id': job_id, 'status': 'completed'}
        mock_storage.get_result.return_value = '# Done'
        
        url = reverse('protocol_result', kwargs={'job_id': job_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['result_markdown'], '# Done')

    def test_generate_protocol_logic(self):
        from protocols.core.utils import generate_protocol
        meta_data = {
            'guild_id': 123,
            'start_time': '2026-01-30T21:46:00.000000',
            'end_time': '2026-01-30T21:47:00.000000',
            'users': {
                '1': {'name': 'Alice', 'channel': 0}
            },
            'events': [
                {'timestamp': '2026-01-30T21:46:05.000000', 'message': 'Event 1'}
            ]
        }
        transcriptions = [
            {'timestamp': 10.0, 'user_id': '1', 'user_name': 'Alice', 'text': 'Hello'}
        ]
        template = "# {{ meta.guild_id }}\n{% for item in timeline %}{{ item.timestamp.strftime('%H:%M:%S') }}: {{ item.content or item.text }}\n{% endfor %}"
        
        result = generate_protocol(meta_data, transcriptions, template)
        self.assertIn('21:46:05: Event 1', result)
        self.assertIn('21:46:10: Hello', result)

class EngineTests(SimpleTestCase):
    def test_factory_whisper(self):
        from protocols.core.engines.factory import get_stt_engine
        from protocols.core.engines.whisper import WhisperEngine
        with self.settings(STT_ENGINE='whisper'):
            with patch('protocols.core.engines.whisper.WhisperEngine.__init__', return_value=None):
                engine = get_stt_engine()
                self.assertIsInstance(engine, WhisperEngine)

    def test_factory_mock(self):
        from protocols.core.engines.factory import get_stt_engine
        from protocols.core.engines.mock import MockEngine
        with self.settings(STT_ENGINE='mock'):
            engine = get_stt_engine()
            self.assertIsInstance(engine, MockEngine)
            
            import numpy as np
            data = np.zeros((100, 2))
            users = {'1': {'name': 'User1', 'channel': 0}}
            result = engine.transcribe(data, 16000, users)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['text'], 'This is a mock transcription.')
