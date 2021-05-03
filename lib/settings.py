import os

class Settings(object):
    bot_id = os.environ.get("MY_BOT_ID")
    bot_name = os.environ.get("MY_BOT_NAME")
    token = os.environ.get("MY_BOT_TOKEN")
    secret_phrase = os.environ.get("MY_SECRET_PHRASE")
    port = os.environ.get("PORT", os.environ.get("MY_BOT_PORT"))

    client_id=os.environ.get("MY_CLIENT_ID")
    client_secret=os.environ.get("MY_CLIENT_SECRET")
    base_uri=os.environ.get("MY_BASE_URI")
    redirect_uri=base_uri + os.environ.get("MY_REDIRECT_URI")
    scopes=os.environ.get("MY_SCOPES")

    mongo_db=os.environ.get("MY_MONGO_URL")
    db_name=os.environ.get("MY_MONGO_DB")
