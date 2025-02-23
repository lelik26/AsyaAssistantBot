
import openai
from utils.logger import setup_logger
from utils.api_utils import async_openai_error_handler
import config as cfg  # Должны быть: OPENAI_API_KEY, ASSISTANT_ID, INSTRUCTION_ASSISTANT, MODELS_GPT

logger = setup_logger(__name__)

class ResponseAssistantError(Exception):
    """Кастомное исключение для ошибок генерации текста."""
    pass

class ResponseAssistantAll:
    """Service for generating text using OpenAI GPT models."""

    def __init__(self):
        """Проверяет конфигурацию API-ключа."""
        self.validate_response_config()
        openai.api_key = cfg.OPENAI_API_KEY

    @staticmethod
    def validate_response_config():
        """Validates that required configuration for text generation is present.

                Raises:
                    ValueError: If API key or models are not configured.
                """
        if not cfg.OPENAI_API_KEY:
            raise ValueError("Не задан API-ключ OpenAI.")
        if not hasattr(cfg, "MODELS_GPT") or not cfg.MODELS_GPT:
            raise ValueError("Не заданы доступные модели GPT.")

    @staticmethod
    def validate_model(model: str) -> bool:
        """Проверяет, поддерживается ли выбранная модель.Args:
            model (str): The model name.

        Returns:
            bool: True if supported, False otherwise.
        """
        return model in cfg.MODELS_GPT

    async def text_generation(self, update, context, user_message: str, model: str = "gpt-4o") -> str:
        """Генерирует текст на основе сообщения пользователя с использованием OpenAI GPT.Args:
            Generates text based on the user's message using OpenAI GPT.

        Args:
            update: Telegram update.
            context: Telegram context.
            user_message (str): The user's input.
            model (str, optional): The model to use. Defaults to "gpt-4o".

        Returns:
            str: Generated text with token usage statistics.

        Raises:
            ResponseAssistantError: If generation fails."""

        if not user_message or not isinstance(user_message, str):
            raise ValueError("❌ Пожалуйста, введите текст для генерации ответа.")
        if len(user_message) > 16000:
            raise ValueError("Текст запроса не должен превышать 16000 символов.")
        if not self.validate_model(model):
            raise ValueError(f"Выбранная модель '{model}' не поддерживается.")

        status_message = await update.message.reply_text("⏳ Ассистент обрабатывает ваш запрос...")
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1000
        )
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        generated_text = response.choices[0].message.content

        result_message = (
            f"{generated_text}\n\n"
            f"🔹 *Статистика токенов:*\n"
            f"📥 Входящие: {input_tokens}\n"
            f"📤 Исходящие: {output_tokens}\n"
            f"💰 Всего: {total_tokens}"
        )
        await status_message.edit_text("✅ Ответ готов!")
        logger.info(
            f"Сгенерированный текст: {generated_text[:50]}... (Входящие: {input_tokens}, "
            f"Исходящие: {output_tokens}, Всего: {total_tokens})"
        )
        return result_message



