import os

flask_secret_key = os.environ["FLASK_SECRET_KEY"]

finbif_api_token = os.environ["FINBIF_API_TOKEN"]

mongodb_server = os.environ.get("MONGODB_SERVER", "")
mongodb_user = os.environ.get("MONGODB_USER", "")
mongodb_pass = os.environ.get("MONGODB_PASS", "")

redis_host = os.environ["REDIS_HOST"]
redis_user = os.environ.get("REDIS_USER", "")
redis_pass = os.environ["REDIS_PASS"]
redis_port = os.environ.get("REDIS_PORT", "10328")

telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
telegram_bot_chat_id = os.environ.get("TELEGRAM_BOT_CHAT_ID", "")

dev_secret = int(os.environ.get("DEV_SECRET", "0"))

bird_secret = os.environ.get("BIRD_SECRET", "")
bird_url = os.environ.get("BIRD_URL", "")
bird_class = os.environ.get("BIRD_CLASS", "")

newsapi_key = os.environ.get("NEWSAPI_KEY", "")
openai_api_key = os.environ["OPENAI_API_KEY"]

flush_secret = os.environ.get("FLUSH_SECRET", "")

digitransit_api_key = os.environ.get("DIGITRANSIT_API_KEY", "")
