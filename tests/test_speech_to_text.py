# tests/test_speech_to_text.py
import unittest
from unittest.mock import patch, mock_open
from services.speech_to_text import SpeechToTextService, SpeechToTextError

class TestSpeechToTextService(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake audio data")
    def test_transcribe_audio_success(self, mock_file):
        service = SpeechToTextService()
        with patch("openai.audio.transcriptions.create") as mock_transcription:
            # Создаем фиктивный объект с атрибутом text
            mock_transcription.return_value = type("Transcription", (), {"text": "Hello world"})
            result = service.transcribe_audio("dummy_path.mp3")
            self.assertEqual(result, "Hello world")

if __name__ == "__main__":
    unittest.main()
