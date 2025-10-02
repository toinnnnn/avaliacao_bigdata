import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

print("Client ID:", client_id)
print("Client Secret:", "****" if client_secret else "MISSING")

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-read-private playlist-read-collaborative"
))

playlist_id = "2Y1AD7uedwsVvCrLYQmqTI"  # sem espaços ou query string
results = sp.playlist_items(playlist_id, limit=5)
for item in results["items"]:
    track = item["track"]
    print(track["name"], "-", track["artists"][0]["name"])
