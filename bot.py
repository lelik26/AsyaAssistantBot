# bot.py
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import config as cfg
from handlers.response_handler import ResponseHandler
from handlers.translation_handler import TranslationHandlers
from handlers.voice_handler import VoiceHandlers
from handlers.speech_handler import SpeechHandler
from handlers.image_handler import ImageHandler
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AsyaAssistantBot:
    """Main class for the AsyaAssistantBot."""

    def __init__(self):
        """Инициализирует бота и необходимые компоненты."""
        self.app = Application.builder().token(cfg.TELEGRAM_BOT_TOKEN).connect_timeout(30).read_timeout(60).build()
        self.translation_handlers = TranslationHandlers()
        self.response_handlers = ResponseHandler()
        self.image_handlers = ImageHandler()
        self.speech_handlers = SpeechHandler()
        self.voice_handlers = VoiceHandlers()



    def setup_handlers(self):
        """Настраивает обработчики команд и сообщений бота."""
        # Обработчики команд
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(self.response_handlers.get_handler())
        self.app.add_handler(self.translation_handlers.get_conversation_handler())
        self.app.add_handler(self.image_handlers.get_handler())
        self.app.add_handler(self.speech_handlers.get_handler())



        # Добавляем обработчик команды /voice (из VoiceHandlers.get_handlers())
        for handler in self.voice_handlers.get_handlers():
            self.app.add_handler(handler)

        # Обработчик для выбора голоса (если сообщение совпадает с названием голоса)
        self.app.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(f"^({'|'.join(cfg.VOICES_GPT.keys())})$"),
            self.voice_handlers.voice_selected
        ))
        # Обработчик для генерации аудио (если текст не является командой и не совпадает с названием голоса)
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND &
            ~filters.Regex(f"^({'|'.join(cfg.VOICES_GPT.keys())})$") &
            ~filters.Regex(f"^({'|'.join(cfg.SUPPORTED_LANGUAGES_FREE)})$") &
            filters.Regex("^/talk$") &
            filters.Regex("^/translate$") &
            filters.Regex("^/image$") &
            filters.Regex("^/speech$") ,
            self.voice_handlers.generate_voice
        ))

        self.app.add_handler(MessageHandler(
            filters.VOICE & filters.AUDIO & ~filters.COMMAND,
            self.speech_handlers.speech_service
        ))



    async def start(self, update: Update, context: CallbackContext) -> None:
        """Обрабатывает команду /start."""
        welcome_text = (
            "👋 Привет! Я твой полезный помощник, могу работать с текстами, рисовать, обрабатывать аудио в текст -доступно не менее 11 языков, озвучивать текст-доступно 8 голосов.\n"
            "Используй команды, чтобы взаимодействовать со мной:\n\n"
            "💬 /talk - Общение с ассистентом.\n"
            "📖 /translate - Перевод текста.\n"
            "🖼 /image - Генерация изображений.\n"   
            "🎙 /speech - Распознавание речи.\n"
            "🔊 /voice - Озвучивание текста.\n"
            "❌ /cancel-Отменяет действия и осуществляет 🔚 выход из диалогов.\n"
            "ℹ️ /help - Помощь."
        )
        await update.message.reply_text(welcome_text)
        logger.info(f"Пользователь {update.effective_user.id} начал работу с ботом.")

    async def help_command(self, update: Update, context: CallbackContext):
        """Отправляет пользователю список команд и информацию о поддержке."""
        help_text = (
            "ℹ️ **Помощь**\n\n"
            "Я твой языковой помощник! Вот что я умею:\n\n"
            "💬 /talk - Общение с ассистентом.\n"
            "📖 /translate - Перевод текста.\n"
            "🖼 /image - Генерация изображений.\n"   
            "🎙 /speech - Распознавание речи.\n"
            "🔊 /voice - Озвучивание текста.\n"
            "❌ /cancel-Отменяет действия и осуществляет 🔚 выход из диалогов.\n"
            "ℹ️ /help - Помощь."
            "💬 **Связаться с поддержкой**: [Написать в поддержку](https://t.me/i_VAN_79)"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown", disable_web_page_preview=True)

    async def set_bot_commands(self):
        """Устанавливает команды для быстрого выбора в Telegram."""
        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand("talk", "Общение с ассистентом"),
            BotCommand("translate", "Перевод текста"),
            BotCommand("image", "Генерация изображений"),
            BotCommand("speech", "Распознавание речи"),
            BotCommand("voice", "Озвучивание текста"),
            BotCommand("cancel", "Отменяет действия"),
            BotCommand("help", "Помощь и техподдержка")
        ]
        tg_bot = self.app.bot if self.app.bot else await self.app.get_bot()
        await tg_bot.set_my_commands(commands)
        logger.info("Команды бота установлены.")


async def main():
    bot = AsyaAssistantBot()
    bot.setup_handlers()
    await bot.app.initialize()
    await bot.set_bot_commands()
    # Удаляем webhook, если он был установлен ранее
    await bot.app.bot.delete_webhook(drop_pending_updates=True)
    await bot.app.start()
    await bot.app.updater.start_polling()
    logger.info("Бот запущен и готов к работе.")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await bot.app.stop()


if __name__ == "__main__":
    asyncio.run(main())
