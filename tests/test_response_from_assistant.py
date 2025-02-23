# tests/test_response_from_assistant.py
import unittest
from unittest.mock import patch
from services.response_from_assistant import ResponseAssistantAll, ResponseAssistantError

class TestResponseAssistantAll(unittest.TestCase):
    def setUp(self):
        self.assistant = ResponseAssistantAll()

    @patch("services.response_from_assistant.openai.chat.completions.create")
    def test_text_generation_success(self, mock_create):
        """Тест успешной генерации текста от ассистента."""
        mock_create.return_value.choices = [{"message": {"content": "Hello, how can I help you?"}}]
        mock_create.return_value.usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        result = self.assistant.text_generation(None, None, "Hello", model="gpt-4o")
        self.assertIn("Hello, how can I help you?", result)
        self.assertIn("📥 Входящие: 10", result)
        self.assertIn("📤 Исходящие: 20", result)
        self.assertIn("💰 Всего: 30", result)

    @patch("services.response_from_assistant.openai.chat.completions.create")
    def test_text_generation_api_error(self, mock_create):
        """Тест обработки ошибки API при генерации текста."""
        mock_create.side_effect = Exception("API Error")
        with self.assertRaises(ResponseAssistantError):
            self.assistant.text_generation(None, None, "What is AI?", model="gpt-4o")

    def test_invalid_model(self):
        """Тест неподдерживаемой модели."""
        with self.assertRaises(ValueError):
            self.assistant.text_generation(None, None, "Tell me a joke", model="invalid-model")

    def test_long_message(self):
        """Тест слишком длинного сообщения (более 16000 символов)."""
        long_text = "A" * 16001
        with self.assertRaises(ValueError):
            self.assistant.text_generation(None, None, long_text, model="gpt-4o")

if __name__ == "__main__":
    unittest.main()
