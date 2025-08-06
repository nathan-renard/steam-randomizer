import os
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
REDIRECT_URI = "http://localhost:8080/"
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

def get_steam_login_url():
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": REDIRECT_URI,
        "openid.realm": REDIRECT_URI,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return f"{STEAM_OPENID_URL}?{urllib.parse.urlencode(params)}"

def extract_steamid(openid_url):
    return openid_url.split("/")[-1]

class SteamAuthHandler(BaseHTTPRequestHandler):
    steamid = None
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "openid.identity" in qs:
            SteamAuthHandler.steamid = extract_steamid(qs["openid.identity"][0])
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Steam login successful. You may close this window.")
        else:
            self.send_response(400)
            self.end_headers()

def run_server():
    httpd = HTTPServer(('localhost', 8080), SteamAuthHandler)
    httpd.handle_request()

def get_zero_hour_games(steamid):
    url = (
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        f"?key={STEAM_API_KEY}&steamid={steamid}&include_appinfo=1&include_played_free_games=1"
    )
    r = requests.get(url)
    data = r.json()
    games = data.get("response", {}).get("games", [])
    zero_hour_games = [g for g in games if g.get("playtime_forever", 1) == 0]
    for game in zero_hour_games:
        print(game.get("name", "Unknown"))

def main():
    if STEAM_API_KEY is None:
        print("STEAM_API_KEY not set in environment.")
        return
    auth_thread = threading.Thread(target=run_server)
    auth_thread.start()
    webbrowser.open(get_steam_login_url())
    auth_thread.join()
    steamid = SteamAuthHandler.steamid
    if steamid:
        print("Games with 0 hours played:")
        get_zero_hour_games(steamid)
    else:
        print("Steam login failed.")

if __name__ == "__main__":
    main()
