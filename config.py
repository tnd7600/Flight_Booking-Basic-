from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.environ.get("DB_URL")
SENDER_EMAIL_ID = os.environ.get("SENDER_EMAIL_ID")
EMAIL_PASSKEY = os.environ.get("EMAIL_PASSKEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
