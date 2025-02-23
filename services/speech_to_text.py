# services/speech_to_text.py
import openai
from pydub import AudioSegment
from utils.logger import setup_logger
from utils.api_utils import sync_openai_error_handler
import config as cfg


logger = setup_logger(__name__)

# Указываем `pydub`, где искать ffmpeg и ffprobe
AudioSegment.converter = cfg.FFMPEG_PATH
AudioSegment.ffprobe = cfg.FFPROBE_PATH
AudioSegment.ffmpeg = cfg.FFMPEG_PATH

class SpeechToTextError(Exception):
    """Кастомное исключение для ошибок перевода."""
    pass

class SpeechToTextService:
    """Service for transcribing audio using OpenAI Whisper."""

    def __init__(self):
        """Инициализирует сервис распознавания речи."""
        self.validate_config()
        openai.api_key = cfg.OPENAI_API_KEY

    @staticmethod
    def validate_config():
        """Validates that OpenAI API key is set.

                Raises:
                    ValueError: If API key is not set.
                """
        if not openai.api_key:
            raise ValueError("Не задан API-ключ OpenAI.")

    @sync_openai_error_handler
    def transcribe_audio(self, audio_file_path: str, model: str = "whisper-1") -> str:
        """Transcribes an audio file to text using OpenAI Whisper.

        Args:
            audio_file_path (str): Path to the audio file.
            model (str, optional): The transcription model. Defaults to "whisper-1".

        Returns:
            str: Transcribed text.

        Raises:
            SpeechToTextError: If transcription fails.
        """
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model=model,
                file=audio_file,
                temperature=0.2
            )
        return response.text