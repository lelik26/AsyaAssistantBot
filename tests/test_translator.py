# tests/test_translator.py
import unittest
import httpx
from unittest.mock import patch
from services.translator import DeepLTranslator, TranslationError

class TestDeepLTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = DeepLTranslator()

    @patch('services.translator.httpx.post')
    def test_valid_translation(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"translations": [{"text": "Привет, мир!"}]}
        result = self.translator.translate("Hello, world!", "RU")
        self.assertEqual(result, "Привет, мир!")

    def test_invalid_language(self):
        with self.assertRaises(ValueError):
            self.translator.translate("Test", "XX")

    def test_empty_text(self):
        with self.assertRaises(ValueError):
            self.translator.translate("", "RU")

    @patch('services.translator.httpx.post')
    def test_api_failure(self, mock_post):
        mock_post.side_effect = Exception("DeepL API недоступен")
        with self.assertRaises(TranslationError) as context:
            self.translator.translate("Hello", "RU")
        self.assertIn("Сервис перевода недоступен", str(context.exception))

if __name__ == "__main__":
    unittest.main()
