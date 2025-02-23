# handlers/voice_handler.py
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from utils.logger import setup_logger
import config as cfg
from services.voices import VoicesService, VoicesError
from utils.file_utils import ensure_directory, get_abs_path

logger = setup_logger(__name__)

# Определяем состояния диалога
WAITING_FOR_VOICE_SELECTION, WAITING_FOR_TEXT_INPUT = range(2)

class VoiceHandlers:
    """Handles text-to-speech operations using OpenAI TTS."""

    def __init__(self):
        """Инициализирует обработчики голосового взаимодействия."""
        self.voice_service = VoicesService()
        self.voices = cfg.VOICES_GPT

    def get_handlers(self):
        """Возвращает список обработчиков команды /voice."""
        return [ConversationHandler(
            entry_points=[CommandHandler("voice", self.choose_voice)],
            states={
                WAITING_FOR_VOICE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.voice_selected),
                    CommandHandler("cancel", self.cancel_voice)
                ],
                WAITING_FOR_TEXT_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.generate_voice),
                    CommandHandler("cancel", self.cancel_voice)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_voice)]
        )]

    def create_voice_keyboard(self) -> ReplyKeyboardMarkup:
        """Создает клавиатуру для выбора голоса.
        Returns:
            ReplyKeyboardMarkup: Keyboard for voice selection."""

        buttons = [[name] for name in self.voices.keys()]
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

    async def choose_voice(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /voice для выбора голоса.
        Prompts the user to choose a voice for TTS.

        Args:
            update (Update): Telegram update.
            context (CallbackContext): Telegram context."""

        keyboard = self.create_voice_keyboard()
        await update.message.reply_text("🎙 Выберите голос для озвучивания:", reply_markup=keyboard)
        return WAITING_FOR_VOICE_SELECTION

    async def voice_selected(self, update: Update, context: CallbackContext):
        """Сохраняет выбранный голос и просит ввести текст.
        Args:
            update (Update): Telegram update.
            context (CallbackContext): Telegram context."""

        selected_voice = update.message.text
        if selected_voice in self.voices:
            context.user_data["selected_voice"] = selected_voice  # Сохраняем выбранный голос
            await update.message.reply_text(
                f"✅ Вы выбрали голос: 🔊 {selected_voice}.\n💬 Теперь введите текст для дальнейших команд.",
                reply_markup=ReplyKeyboardRemove()
            )
            return WAITING_FOR_TEXT_INPUT
        else:
            await update.message.reply_text("❌ Пожалуйста, выберите голос из предложенного списка.")
            return WAITING_FOR_VOICE_SELECTION

    async def generate_voice(self, update: Update, context: CallbackContext):
        """Генерирует аудио из текста с помощью выбранного голоса и отправляет его пользователю.
        Args:
            update (Update): Telegram update.
            context (CallbackContext): Telegram context."""

        selected_voice = context.user_data.get("selected_voice")
        if not selected_voice:
            await update.message.reply_text("⚠️ Сначала выберите голос с помощью команды /voice.")
            return WAITING_FOR_VOICE_SELECTION

        text = update.message.text

        try:
            voice_id = self.voices.get(selected_voice)
            if voice_id is None:
                await update.message.reply_text("❌ Ошибка: выбранный голос не найден.")
                return WAITING_FOR_VOICE_SELECTION

            await update.message.reply_text(f"⌛️Начинаю обработку текста и формирую аудиофайл после озвучивания... ")

            # Папка для аудиофайлов
            audio_dir = get_abs_path("static/audio_file")
            ensure_directory(audio_dir)

            audio_file_path = os.path.join(audio_dir, f"{update.message.message_id}.mp3")

            # audio_file = self.voice_service.generate_audio(text, voice_id)
            # Генерация аудиофайла
            self.voice_service.generate_audio(text, voice_id, audio_file_path)

            with open(audio_file_path, "rb") as audio:
                await update.message.reply_audio(audio=audio)
            logger.info(f"Аудио отправлено пользователю {update.effective_user.id}.")

            # Удаление файла после отправки
            os.remove(audio_file_path)
            logger.info(f"Аудиофайл {audio_file_path} удалён.")

            await update.message.reply_text(
                "💡Чтобы продолжить дальше работать с голосом выберите команду /voice. \n"
                "Если хотите перейти в другой диалог выберите /start или любую другую команду для начала диалога ",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

        except VoicesError as e:
            logger.error(f"Ошибка при генерации аудио для пользователя {update.effective_user.id}: {str(e)}")
            await update.message.reply_text("❌ Произошла ошибка при генерации аудио. Попробуйте позже.")
            return WAITING_FOR_TEXT_INPUT

    async def cancel_voice(self, update: Update, context: CallbackContext) -> int:
        """Отменяет процесс озвучивания."""
        await update.message.reply_text(
            "❌ Озвучивание отменено. \n"
            "Выберите команду /voice или /start ,любую другую команду для начала диалога ",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
