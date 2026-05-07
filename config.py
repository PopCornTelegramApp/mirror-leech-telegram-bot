from os import getenv

BOT_TOKEN              = getenv("BOT_TOKEN", "")
OWNER_ID               = int(getenv("OWNER_ID", "0"))
TELEGRAM_API           = int(getenv("TELEGRAM_API", "0"))
TELEGRAM_HASH          = getenv("TELEGRAM_HASH", "")
DEFAULT_UPLOAD         = "tg"
LEECH_DUMP_CHAT        = getenv("LEECH_DUMP_CHAT", "")
TMDB_API_KEY           = getenv("TMDB_API_KEY", "")
POPCORN_CHANNEL_ID     = int(getenv("POPCORN_CHANNEL_ID", "0"))
POPCORN_POST_TO_CHANNEL = getenv("POPCORN_POST_TO_CHANNEL", "True") == "True"
LEECH_FILENAME_PREFIX  = "🍿"
AS_DOCUMENT            = False
MEDIA_GROUP            = True
BASE_URL_PORT          = int(getenv("PORT", "8080"))
STATUS_LIMIT           = 4
STATUS_UPDATE_INTERVAL = 15
