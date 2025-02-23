# services/translator.py
import httpx
from typing import Any
import config as cfg
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TranslationError(Exception):
    """Кастомное исключение для ошибок перевода."""
    pass

class DeepLTranslator:
    """Service for translating text using DeepL API."""

    def __init__(self):
        """Инициализирует переводчик и проверяет конфигурацию."""
        self.validate_translator_config()

    @staticmethod
    def validate_translator_config():
        """Проверяет наличие необходимых настроек для работы переводчика.
        Raises:
            ValueError: If API key or URL is not set."""
        if not cfg.DEEPL_API_KEY_FREE:
            raise ValueError("Не задан ключ API для DeepL.")
        if not cfg.DEEPL_API_FREE_URL:
            raise ValueError("Не задан URL API для DeepL.")

    @staticmethod
    def validate_language(target_lang: str) -> bool:
        """Проверяет, поддерживается ли указанный язык перевода.
        Args:
            target_lang (str): The target language code.

        Returns:
            bool: True if supported, False otherwise."""
        return target_lang in cfg.SUPPORTED_LANGUAGES_FREE.values()

    def translate(self, text: str, target_lang: str) -> str:
        """Переводит заданный текст на указанный язык.
        Args:
            text (str): Text to translate.
            target_lang (str): Target language code.

        Returns:
            str: Translated text.

        Raises:
            TranslationError: If translation fails."""
        if not text or not isinstance(text, str):
            raise ValueError("Некорректный текст для перевода.")
        if len(text) > 10000:
            raise ValueError("Текст слишком длинный для перевода (максимум 10000 символов).")
        if not self.validate_language(target_lang):
            raise ValueError(f"Неподдерживаемый язык перевода: {target_lang}")

        try:
            headers = {"Authorization": f"DeepL-Auth-Key {cfg.DEEPL_API_KEY_FREE}"}
            data = {"text": text, "target_lang": target_lang}
            response = httpx.post(cfg.DEEPL_API_FREE_URL, headers=headers, data=data)
            response.raise_for_status()
            json_response = response.json()
            if "translations" not in json_response or not json_response["translations"]:
                raise TranslationError("Ошибка при получении переведенного текста.")
            translated_text = json_response["translations"][0]["text"]

            logger.info(f"Успешный перевод текста: '{text[:20]}...' -> '{translated_text[:20]}...'")
            return translated_text
        except httpx.HTTPError as e:
            logger.error(f"Ошибка HTTP при обращении к DeepL API: {str(e)}")
            raise TranslationError("Сервис перевода недоступен.")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при переводе: {str(e)}")
            raise TranslationError("Произошла ошибка при обработке перевода.")