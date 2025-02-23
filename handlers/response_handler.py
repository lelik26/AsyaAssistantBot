# handlers/response_handler.py
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from utils.logger import setup_logger
from services.response_from_assistant import ResponseAssistantAll, ResponseAssistantError

logger = setup_logger(__name__)

# Определяем состояние диалога
WAITING_FOR_MESSAGE = 1

class ResponseHandler:
    """Handles conversation with the AI for text generation."""

    def __init__(self):
        """Инициализирует обработчики общения с AI."""
        self.response_service = ResponseAssistantAll()

    def get_handler(self):
        """Returns a ConversationHandler for /talk command."""
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("talk", self.start_talking)],
            states={
                WAITING_FOR_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.generate_response),
                    MessageHandler(filters.COMMAND, self.cancel_talk)  # Добавляем выход из диалога
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_talk)]
        )
        return conv_handler

    async def start_talking(self, update: Update, context: CallbackContext):
        """Starts the conversation by asking the user to send a message.
               Args:
                   update (Update): Telegram update.
                   context (CallbackContext): Telegram context.

               Returns:
                   int: Next conversation state.
               """
        await update.message.reply_text("💬 Напишите что-нибудь, и я отвечу!")
        return WAITING_FOR_MESSAGE

    async def generate_response(self, update: Update, context: CallbackContext):
        """Generates a response from the AI based on user input.

               Args:
                   update (Update): Telegram update.
                   context (CallbackContext): Telegram context.

               Returns:
                   int: Conversation end state.
               """
        user_message = update.message.text
        try:
            response = await self.response_service.text_generation(update, context, user_message)

            await update.message.reply_text(response, parse_mode="Markdown")
            logger.info(f"Ответ отправлен пользователю {update.effective_user.id}.")
        except ResponseAssistantError as e:
            logger.error(f"Ошибка генерации текста для {update.effective_user.id}: {str(e)}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        return WAITING_FOR_MESSAGE #ConversationHandler.END

    async def cancel_talk(self, update: Update, context: CallbackContext):
        """Завершает диалог, если пользователь вводит другую команду.Cancels the conversation.

               Args:
                   update (Update): Telegram update.
                   context (CallbackContext): Telegram context.

               Returns:
                   int: Conversation end state.
               """
        await update.message.reply_text("🔚 Вы вышли из диалога. \n"
                                        "Выберите команду /talk или /start ,любую другую команду для начала диалога ")
        return ConversationHandler.END

