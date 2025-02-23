# handlers/speech_handler.py
import os
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from utils.logger import setup_logger
from utils.file_utils import ensure_directory, get_abs_path
from services.speech_to_text import SpeechToTextService, SpeechToTextError
from pydub import AudioSegment
import config as cfg

# Указываем `pydub`, где искать ffmpeg и ffprobe
AudioSegment.converter = cfg.FFMPEG_PATH
AudioSegment.ffprobe = cfg.FFPROBE_PATH
AudioSegment.ffmpeg = cfg.FFMPEG_PATH


logger = setup_logger(__name__)

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MAX_DURATION = 5400 # максимум 5400 секунд (90 минут)
WAITING_FOR_VOICE = 1

def get_audio_duration(file_path: str) -> float:
    """Returns the duration of an audio file in seconds.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        float: Duration in seconds.
    """
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000

class SpeechHandler:
    """Handles speech recognition using OpenAI Whisper API."""

    def __init__(self):
        self.speech_service = SpeechToTextService()

    def get_handler(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("speech", self.start_speech)],
            states={
                WAITING_FOR_VOICE: [
                    MessageHandler(filters.VOICE | filters.AUDIO, self.process_speech),
                    MessageHandler(filters.COMMAND, self.cancel_speech)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_speech)]
        )
        return conv_handler

    async def start_speech(self, update: Update, context: CallbackContext) -> int:
        """Prompts the user to send an audio message for transcription.

               Args:
                   update (Update): Telegram update.
                   context (CallbackContext): Telegram context.

               Returns:
                   int: Next conversation state.
               """
        await update.message.reply_text("🎙 Отправьте голосовое сообщение, и я его расшифрую.")
        return WAITING_FOR_VOICE

    async def process_speech(self, update: Update, context: CallbackContext) -> int:
        """Processes the received audio, checks duration, transcribes and sends the result.

                Args:
                    update (Update): Telegram update.
                    context (CallbackContext): Telegram context.

                Returns:
                    int: Conversation end state.
                """

        audio_obj = None
        expected_extension = "ogg"  # по умолчанию для голосовых сообщений

        if update.message.voice:
            audio_obj = update.message.voice
            expected_extension = "ogg"
        elif update.message.audio:
            audio_obj = update.message.audio
            allowed_mime_types = {
                "audio/mpeg", "audio/mp3", "audio/mp4", "audio/ogg",
                "audio/webm", "audio/m4a", "audio/wav", "audio/mpga"
            }
            if audio_obj.mime_type not in allowed_mime_types:
                await update.message.reply_text(
                    "❌ Неверный формат аудиофайла. Пожалуйста, отправьте файл в формате mp3, ogg или wav."
                )
                return WAITING_FOR_VOICE
            if "mpeg" in audio_obj.mime_type or "mp3" in audio_obj.mime_type:
                expected_extension = "mp3"
            else:
                expected_extension = "ogg"
        else:
            await update.message.reply_text("❌ Пожалуйста, отправьте голосовое сообщение или аудиофайл.")
            return WAITING_FOR_VOICE

        if audio_obj.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                "❌ Файл слишком большой (более 25 MB). Пожалуйста, отправьте файл меньшего размера."
            )
            return WAITING_FOR_VOICE

        # Формируем абсолютный путь для файла
        audio_dir = get_abs_path("static/audio_file")
        ensure_directory(audio_dir)
        audio_file_path = os.path.join(audio_dir, f"{audio_obj.file_id}.{expected_extension}")


        try:
            # Получаем объект файла
            audio_obj = await audio_obj.get_file()
            # Скачиваем файл
            await audio_obj.download_to_drive(audio_file_path)
            logger.info(f"Файл скачивается в: {audio_file_path}")

            # Информируем пользователя о длительной операции
            status_msg = await update.message.reply_text("⌛️ Обработка аудио, пожалуйста, подождите...")
            # Увеличиваем задержку, чтобы убедиться, что файл создан
            await asyncio.sleep(25)


            # Проверяем нахождение аудио файла по пути
            if not os.path.exists(audio_file_path):
                logger.error(f"Файл не найден по пути: {audio_file_path}")
                await update.message.reply_text("❌ Не удалось скачать аудиофайл.")
                return WAITING_FOR_VOICE

            # Проверяем продолжительность аудио не более 90 минут
            duration = get_audio_duration(audio_file_path)
            if duration > MAX_DURATION:
                await update.message.reply_text(
                    f"❌ Аудиофайл слишком длинный ({duration:.1f} сек.). Максимум {MAX_DURATION} сек.")
                return WAITING_FOR_VOICE


            recognized_text = self.speech_service.transcribe_audio(audio_file_path)
            await status_msg.edit_text("✅ Аудио обработано!")
            await update.message.reply_text(f"📝 Распознанный текст:\n{recognized_text}")
            logger.info(f"Распознанная речь отправлена пользователю {update.effective_user.id}.")

            text_dir = get_abs_path("static/recognized_text_file")
            ensure_directory(text_dir)
            text_file_path = os.path.join(text_dir, f"{audio_obj.file_id}.txt")
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(recognized_text)
            #
            # with open(text_file_path, "rb") as doc:
            #     await update.message.reply_document(document=doc, filename=f"{audio_obj.file_id}.txt")

            # Удаление файла после обработки
            os.remove(audio_file_path)
            os.remove(text_file_path)
            logger.info(f"Аудиофайл {audio_file_path} и Текстовый файл {text_file_path} удалёны.")

        except SpeechToTextError as e:
            logger.error(f"Ошибка распознавания речи у {update.effective_user.id}: {str(e)}")
            await update.message.reply_text("❌ Ошибка при распознавании речи. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Ошибка обработки аудиофайла: {str(e)}")
            await update.message.reply_text("❌ Ошибка при обработке аудиофайла. Попробуйте позже.")

        return WAITING_FOR_VOICE

    async def cancel_speech(self, update: Update, context: CallbackContext):
        """Завершает диалог, если пользователь вводит другую команду.Cancels the conversation.

               Args:
                   update (Update): Telegram update.
                   context (CallbackContext): Telegram context.

               Returns:
                   int: Conversation end state.
               """
        await update.message.reply_text("🔚 Вы вышли из диалога. \n"
                                        "Выберите команду /speech или /start ,любую другую команду для начала диалога ")
        return ConversationHandler.END
