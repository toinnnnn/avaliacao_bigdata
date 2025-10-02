import os
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

def get_spotify_client():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    return Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-read-private playlist-read-collaborative"
    ))

def fetch_playlist_tracks(sp, playlist_id, limit=100):
    results = sp.playlist_items(playlist_id, limit=limit)
    items = results.get("items", [])
    rows = []
    for it in items:
        t = it["track"]
        if not t:
            continue
        artists = [a["name"] for a in t["artists"]]
        rows.append({
            "track_id": t["id"],
            "name": t["name"],
            "artists": artists,
            "artist": artists[0] if artists else None,
            "album": t["album"]["name"],
            "popularity": t["popularity"],
            "duration_ms": t["duration_ms"],
            "release_date": t["album"].get("release_date")
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    sp = get_spotify_client()
    playlist_id = "2Y1AD7uedwsVvCrLYQmqTI"  # exemplo: sua playlist pessoal
    df = fetch_playlist_tracks(sp, playlist_id, limit=20)
    print(df.head())
