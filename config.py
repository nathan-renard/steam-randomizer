import os
from dotenv import load_dotenv

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

REDIRECT_URI = "http://localhost:8080/"
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
 