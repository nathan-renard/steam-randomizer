import os, webbrowser, threading
from steam_auth_handler import SteamAuthHandler, run_server, get_steam_login_url, get_zero_hour_games
from config import STEAM_API_KEY

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
