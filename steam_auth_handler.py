import urllib.parse, requests, random
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import REDIRECT_URI, STEAM_OPENID_URL, STEAM_API_KEY

class SteamAuthHandler(BaseHTTPRequestHandler):
    steamid = None
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "openid.identity" in qs:
            SteamAuthHandler.steamid = extract_steamid(qs["openid.identity"][0])
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress logging
    
def extract_steamid(openid_url):
    return openid_url.split("/")[-1]

def run_server():
    httpd = HTTPServer(('localhost', 8080), SteamAuthHandler)
    httpd.handle_request()

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

def get_zero_hour_games(steamid):
    url = (
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        f"?key={STEAM_API_KEY}&steamid={steamid}&include_appinfo=1&include_played_free_games=1"
    )
    r = requests.get(url)
    data = r.json()
    games = data.get("response", {}).get("games", [])
    zero_hour_games = [g for g in games if g.get("playtime_forever", 1) == 0]
    
    random_game = random.choice(zero_hour_games) if zero_hour_games else None
    print(f"Random game with 0 hours played: {random_game['name'] if random_game else 'None'}")