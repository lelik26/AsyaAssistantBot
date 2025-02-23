# services/voices.py
import openai
import uuid
from utils.logger import setup_logger
from utils.api_utils import sync_openai_error_handler
import config as cfg

logger = setup_logger(__name__)

class VoicesError(Exception):
    """Custom exception for voice synthesis errors."""
    pass

class VoicesService:
    """Service for generating audio from text using OpenAI TTS."""

    def __init__(self):
        self.validate_voices_config()
        openai.api_key = cfg.OPENAI_API_KEY

    @staticmethod
    def validate_voices_config():
        if not openai.api_key:
            raise ValueError("Не задан API-ключ OpenAI.")

    @sync_openai_error_handler
    def generate_audio(self, text: str, voice: str, audio_file_path: str = None, model: str = "tts-1") -> str:
        """Generates an audio file from text using OpenAI TTS.

        Args:
            text (str): The text to convert.
            voice (str): The voice identifier.
            audio_file_path (str, optional): Full path where to save the audio file.
                                             If not provided, a random filename is generated.
            model (str, optional): The TTS model. Defaults to "tts-1".

        Returns:
            str: Filename of the generated audio.

        Raises:
            VoicesError: If generation fails.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Текст для озвучивания должен быть строкой и не пустым.")
        if len(text) > 4090:
            raise ValueError("Текст для озвучивания не должен превышать 4090 символов.")

        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            speed=1.0,
            input=text
        )
        if not hasattr(response, "content"):
            raise VoicesError("Ошибка: не получен контент аудио.")
        if audio_file_path is None:
            filename = f"audio_{uuid.uuid4()}.mp3"
        else:
            filename = audio_file_path
        with open(filename, "wb") as audio_file:
            audio_file.write(response.content)
        logger.info(f"Аудиофайл {filename} успешно создан.")
        return filename
