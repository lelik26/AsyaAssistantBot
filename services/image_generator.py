# services/image_generator.py
import openai
from utils.logger import setup_logger
from utils.api_utils import sync_openai_error_handler
import config as cfg


logger = setup_logger(__name__)

class ImageGenerationError(Exception):
    """Кастомное исключение для ошибок генерации изображений."""
    pass

class ImageGenerator:
    """Service for generating images using OpenAI image API."""

    def __init__(self):
        """Проверяет конфигурацию API-ключа."""
        self.validate_images_config()
        openai.api_key = cfg.OPENAI_API_KEY

    @staticmethod
    def validate_images_config():
        """Validates that the OpenAI API key is set.

                Raises:
                    ValueError: If API key is not set.
                """
        if not openai.api_key:
            raise ValueError("Не задан API-ключ OpenAI.")

    @staticmethod
    def validate_image_model(model: str) -> bool:
        """Проверяет, поддерживается ли модель TTS.
        Checks if the image generation model is supported.

        Args:
            model (str): Model name.

        Returns:
            bool: True if supported, False otherwise."""
        return model in cfg.IMAGE_MODELS_GPT.values()

    @sync_openai_error_handler
    def generate_image(self, prompt: str, model: str = "dall-e-3") -> str:
        """ Generates an image based on the prompt using OpenAI API.

        Args:
            prompt (str): Description for the image.
            model (str, optional): Image generation model. Defaults to "dall-e-3".

        Returns:
            str: URL of the generated image.

        Raises:
            ImageGenerationError: If generation fails."""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt должен быть непустой строкой.")
        response = openai.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        logger.info(f"Изображение успешно создано: {image_url}")
        return image_url