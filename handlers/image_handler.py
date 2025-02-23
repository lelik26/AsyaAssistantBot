# handlers/image_handler.py
import asyncio
import logging

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from utils.logger import setup_logger
from telegram.error import TimedOut
from services.image_generator import ImageGenerator,ImageGenerationError

logger = setup_logger(__name__)

# Состояние ожидания описания изображения
WAITING_FOR_IMAGE_DESCRIPTION = 1

class ImageHandler:
    """Handles image generation requests using OpenAI image API."""

    def __init__(self):
        """Инициализирует обработчики генерации изображений."""
        self.image_generator = ImageGenerator()

    def get_handler(self):
        """Returns a ConversationHandler for /image command."""
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("image", self.start_image_generation)],
            states={
                WAITING_FOR_IMAGE_DESCRIPTION: [
                    # Обрабатываем только текстовые сообщения (без команд)
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.generate_image_response),
                    MessageHandler(filters.COMMAND, self.cancel_generate_image)

                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_generate_image)],
        )
        return conv_handler

    async def start_image_generation(self, update: Update, context: CallbackContext) -> int:
        """Prompts the user to enter an image description.

               Args:
                   update (Update): Telegram update.
                   context (CallbackContext): Telegram context.

               Returns:
                   int: Next conversation state.
               """
        await update.message.reply_text("🖼 Введите описание изображения, которое хотите создать:")
        return WAITING_FOR_IMAGE_DESCRIPTION

    async def generate_image_response(self, update: Update, context: CallbackContext) -> int:
        """Обрабатывает текстовый запрос пользователя и отправляет сгенерированное изображение.
         Args:
            update (Update): Telegram update.
            context (CallbackContext): Telegram context.

        Returns:
            int: Conversation end state.
        """
        prompt = update.message.text
        await update.message.reply_text(f"🖼 Генерирую изображение... для описания:\n{prompt}")
        try:
            image_url = self.image_generator.generate_image(prompt)
            await update.message.reply_photo(photo=image_url, caption="🖼 Ваше сгенерированное изображение")
            logger.info(f"Изображение отправлено пользователю {update.effective_user.id}.")
        except ImageGenerationError as e:
            logger.error(f"Ошибка генерации изображения для {update.effective_user.id}: {str(e)}")
            await update.message.reply_text("❌ Произошла ошибка при генерации изображения. Попробуйте позже.")
        return WAITING_FOR_IMAGE_DESCRIPTION#ConversationHandler.END

    async def cancel_generate_image(self, update: Update, context: CallbackContext):
        """Отменяет генерацию изображения и выходит из состояния."""
        try:
            await update.message.reply_text(
                "❌ Генерация изображения отменена.\n"
                "🔚 Вы вышли из диалога.\n"
                "Выберите команду /image или /start ,любую другую команду для начала диалога "
            )
        except TimedOut:
            logging.error("Ошибка: Telegram API не ответил вовремя. Повторная отправка...")
            await asyncio.sleep(2)  # Даем немного времени
            try:
                await update.message.reply_text("⚠️ Произошла задержка. Повторная попытка...")
            except Exception as e:
                logging.error(f"Ошибка при повторной отправке сообщения: {e}")

        return ConversationHandler.END
