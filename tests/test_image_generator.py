# tests/test_image_generator.py
import unittest
from unittest.mock import patch
from services.image_generator import ImageGenerator, ImageGenerationError

class TestImageGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ImageGenerator()

    @patch("services.image_generator.openai.images.create")
    def test_generate_image_success(self, mock_create):
        """Тест успешной генерации изображения."""
        mock_create.return_value.data = [{"url": "https://fakeimage.com/image.png"}]
        result = self.generator.generate_image("A cat sitting on the moon")
        self.assertEqual(result, "https://fakeimage.com/image.png")

    @patch("services.image_generator.openai.images.create")
    def test_generate_image_api_error(self, mock_create):
        """Тест ошибки при запросе к OpenAI API."""
        mock_create.side_effect = Exception("API Error")
        with self.assertRaises(ImageGenerationError):
            self.generator.generate_image("A futuristic city")

    def test_invalid_model(self):
        """Тест использования неподдерживаемой модели."""
        with self.assertRaises(ValueError):
            self.generator.generate_image("A dragon in the sky", model="invalid-model")

if __name__ == "__main__":
    unittest.main()
