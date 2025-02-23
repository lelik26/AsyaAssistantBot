# config.py
import os
import shutil
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# API ключи и токены
# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# DeepL
DEEPL_API_KEY_FREE = os.getenv("DEEPL_API_KEY")
DEEPL_API_FREE_URL = os.getenv("DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Пути к ffmpeg и ffprobe
# FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"
# FFPROBE_PATH = "/opt/homebrew/bin/ffprobe"
# Поиск FFmpeg и FFprobe через переменные окружения или системные пути
FFMPEG_PATH = os.getenv('FFMPEG_PATH', shutil.which("ffmpeg"))
FFPROBE_PATH = os.getenv('FFPROBE_PATH', shutil.which("ffprobe"))


# Проверка существования файлов
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError(f"FFmpeg не найден по пути: {FFMPEG_PATH}")
if not os.path.exists(FFPROBE_PATH):
    raise FileNotFoundError(f"FFprobe не найден по пути: {FFPROBE_PATH}")


# Проверяем необходимые переменные окружения
required_env_vars = ["TELEGRAM_BOT_TOKEN", "DEEPL_API_KEY_FREE", "OPENAI_API_KEY"]
for var in required_env_vars:
    if not globals().get(var):
        raise EnvironmentError(f"Переменная окружения {var} не установлена.")

# Модели для генерации текста OpenAI (стоимость указана условно)
MODELS_GPT = {
    "gpt-4o": {"input": 2.50, "output": 10.00, "cached_input": 1.25},
    "gpt-4o-mini": {"input": 0.150, "output": 0.60, "cached_input": 0.075},
    "o1": {"input": 15.00, "output": 60.00, "cached_input": 7.50},
    "o1-mini": {"input": 1.10, "output": 4.40, "cached_input": 0.55},
    "o3-mini": {"input": 1.10, "output": 4.40, "cached_input": 0.55}
}

# Модели для TTS (голосовой синтез)
TTS_MODELS_GPT = {
    "tts-1": {"input": 0, "output": 15.00, "cached_input": 0},
    "tts-1-hd": {"input": 0, "output": 30.00, "cached_input": 0}
}

# Модели для STT (распознавание речи)
STT_MODELS_GPT = {"whisper-1": {"input": 0, "output": 0.006, "cached_input": 0}}

# Модели для генерации изображений
IMAGE_MODELS_GPT = {
    "dall-e-2": {
        "standard": {
            "size": {'256x256': 0.016, '512x512': 0.018, '1024x1024': 0.020}
        }
    },
    "dall-e-3": {
        "standard": {"size": {'1024x1024': 0.04, '1024x1792': 0.08}},
        "hd": {"size": {'1024x1024': 0.08, '1024x1792': 0.12}}
    }
}

# Список доступных голосов GPT
VOICES_GPT = {
    "alloy": "alloy",
    "ash": "ash",
    "coral": "coral",
    "echo": "echo",
    "fable": "fable",
    "onyx": "onyx",
    "nova": "nova",
    "sage": "sage",
    "shimmer": "shimmer"
}

# Языки
SUPPORTED_LANGUAGES_FREE = {
    "🇬🇧 English": "EN",
    "🇷🇺 Русский": "RU",
    "🇨🇳 中文": "ZH",  # Китайский
    "🇹🇷 Türkçe": "TR",
    "🇸🇦 العربية": "AR", # Арабский
    "🇪🇸 Español": "ES",  # Испанский
    "🇵🇹 Português": "PT",  # Португальский
    "🇫🇷 Français": "FR",  # Французский
    "🇩🇪 Deutsch": "DE",  # Немецкий
    "🇮🇹 Italiano": "IT",  # Итальянский
    "🇮🇩 Bahasa Indonesia": "ID",  # Индонезийский
   
}

SUPPORTED_LANGUAGES_FULL = {
    "🇬🇧 English": "EN",
    "🇷🇺 Русский": "RU",
    "🇨🇳 中文": "ZH",  # Китайский
    "🇹🇷 Türkçe": "TR",
    "🇸🇦 العربية": "AR", # Арабский
    "🇪🇸 Español": "ES",  # Испанский
    "🇵🇹 Português": "PT",  # Португальский
    "🇫🇷 Français": "FR",  # Французский
    "🇩🇪 Deutsch": "DE",  # Немецкий
    "🇮🇹 Italiano": "IT",  # Итальянский
    "🇮🇩 Bahasa Indonesia": "ID",  # Индонезийский
    "🇧🇬 Български": "BG",  # Болгарский
    "🇨🇿 Čeština": "CS",  # Чешский
    "🇩🇰 Dansk": "DA",  # Датский
    "🇬🇷 Ελληνικά": "EL",  # Греческий
    "🇪🇪 Eesti": "ET",  # Эстонский
    "🇫🇮 Suomi": "FI",  # Финский
    "🇭🇺 Magyar": "HU",  # Венгерский
    "🇯🇵 日本語": "JA",  # Японский
    "🇰🇷 한국어": "KO",  # Корейский
    "🇱🇹 Lietuvių": "LT",  # Литовский
    "🇱🇻 Latviešu": "LV",  # Латышский
    "🇳🇴 Norsk Bokmål": "NB",  # Норвежский Букмол
    "🇳🇱 Nederlands": "NL",  # Нидерландский
    "🇵🇱 Polski": "PL",  # Польский
    "🇷🇴 Română": "RO",  # Румынский
    "🇸🇰 Slovenčina": "SK",  # Словацкий
    "🇸🇮 Slovenščina": "SL",  # Словенский
    "🇸🇪 Svenska": "SV",  # Шведский
}

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "bot.log"


