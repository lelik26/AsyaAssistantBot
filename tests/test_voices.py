# tests/test_voices.py
import unittest
from unittest.mock import patch
from services.voices import VoicesService, VoicesError

def generate_audio(text, voice):
    service = VoicesService()
    return service.generate_audio(text, voice)

class TestVoices(unittest.TestCase):
    @patch('services.voices.openai.audio.speech.create')
    def test_generate_audio_success(self, mock_create):
        """Тест успешного создания аудио."""
        mock_create.return_value.content = b'audio bytes'
        text = "Hello, world!"
        voice = "alloy"
        filename = generate_audio(text, voice)
        self.assertTrue(filename.startswith("audio_"))
        self.assertTrue(filename.endswith(".mp3"))

    def test_empty_text(self):
        """Тест передачи пустого текста."""
        with self.assertRaises(ValueError):
            generate_audio("", "alloy")

    def test_long_text(self):
        """Тест слишком длинного текста для озвучивания."""
        text = "a" * 5000  # Превышает лимит 4000 символов
        with self.assertRaises(ValueError):
            generate_audio(text, "alloy")

if __name__ == "__main__":
    unittest.main()
