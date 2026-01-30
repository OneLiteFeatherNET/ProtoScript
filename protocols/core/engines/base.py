from abc import ABC, abstractmethod

class STTEngine(ABC):
    def transcribe(self, audio_data, samplerate, users):
        """
        Transcribes audio data for the specified users by splitting into channels.
        """
        transcriptions = []
        for user_id, user_info in users.items():
            channel_idx = user_info.get('channel')
            if channel_idx is not None and channel_idx < audio_data.shape[1]:
                channel_data = audio_data[:, channel_idx]
                channel_transcripts = self.transcribe_channel(channel_data, samplerate)
                for t in channel_transcripts:
                    t.update({
                        'user_id': user_id,
                        'user_name': user_info['name']
                    })
                    transcriptions.append(t)
        return transcriptions

    @abstractmethod
    def transcribe_channel(self, channel_data, samplerate):
        """
        Transcribes a single audio channel.
        :return: List of dictionaries with 'type', 'timestamp', 'text'.
        """
        pass
