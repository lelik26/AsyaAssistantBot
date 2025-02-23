# handlers/translation_handler.py
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.logger import setup_logger
from services.translator import DeepLTranslator, TranslationError
import config as cfg

logger = setup_logger(__name__)

# Определение этапов разговора для ConversationHandler
SELECT_LANGUAGE, GET_TEXT = range(2)

class TranslationHandlers:
    """Handles text translation using DeepL API."""

    def __init__(self):
        """Инициализирует обработчики перевода."""
        self.translator = DeepLTranslator()

    def get_conversation_handler(self):
        """Возвращает ConversationHandler для команды /translate."""
        return ConversationHandler(
            entry_points=[CommandHandler("translate", self.start_translation)],
            states={
                SELECT_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_language)],
                GET_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_text),
                           MessageHandler(filters.COMMAND, self.cancel)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

    async def start_translation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Начинает процесс перевода, предлагая выбрать язык.

        Args:
            update (Update): Telegram update.
            context (ContextTypes.DEFAULT_TYPE): Telegram context.

        Returns:
            int: Next conversation state.
        """
        keyboard = [[key] for key in cfg.SUPPORTED_LANGUAGES_FREE.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("🌐 Пожалуйста, выберите язык для перевода:", reply_markup=reply_markup)
        return SELECT_LANGUAGE

    async def select_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Получает и сохраняет выбранный пользователем язык.

        Args:
            update (Update): Telegram update.
            context (ContextTypes.DEFAULT_TYPE): Telegram context.

        Returns:
            int: Next conversation state.
        """
        selected_language = update.message.text
        if selected_language not in cfg.SUPPORTED_LANGUAGES_FREE:
            await update.message.reply_text("❌ Пожалуйста, выберите язык из предложенного списка.")
            return SELECT_LANGUAGE
        context.user_data["target_lang"] = cfg.SUPPORTED_LANGUAGES_FREE[selected_language]
        await update.message.reply_text("✏️ Введите текст для перевода:", reply_markup=ReplyKeyboardRemove())
        return GET_TEXT

    async def get_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Получает текст от пользователя и выполняет перевод.
        Args:
            update (Update): Telegram update.
            context (ContextTypes.DEFAULT_TYPE): Telegram context.

        Returns:
            int: Conversation end state.
        """
        text_to_translate = update.message.text
        target_lang = context.user_data["target_lang"]
        await update.message.reply_text(f"🔄 Перевожу текст на\n{target_lang}: ")
        try:

            translated_text = self.translator.translate(text_to_translate, target_lang)
            await update.message.reply_text(f"🔄 Перевод на {target_lang}:\n\n{translated_text}")
            logger.info(f"Успешный перевод для пользователя {update.effective_user.id}")
        except Exception as e:
            logger.error(f"Ошибка перевода для пользователя {update.effective_user.id}: {str(e)}")
            await update.message.reply_text("❌😔 Произошла ошибка при переводе текста. Попробуйте позже.")
        return GET_TEXT#ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отменяет процесс перевода.
        Args:
            update (Update): Telegram update.
            context (ContextTypes.DEFAULT_TYPE): Telegram context.

        Returns:
            int: Conversation end state."""
        await update.message.reply_text("❌😱 Перевод отменен.\n"
                                        "🔚 Вы вышли из диалога.\n"
                                        "Выберите команду /translate или /start ,любую другую команду для начала диалога ", reply_markup=ReplyKeyboardRemove())
        logger.info(f"Пользователь {update.effective_user.id} отменил перевод.")
        return ConversationHandler.END

