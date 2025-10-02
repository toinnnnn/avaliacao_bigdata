# src/extract_spotify.py
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Autenticação
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# 🔥 Playlists oficiais do Spotify (Top 50 Global + regionais)
REGIONS = {
    "GLOBAL": "3MtqrQpHawSInQYTitTveL",  # Top 50 Global (novo ID)
    "BR": "0oU481CO1t5yFqDcxfoLkF",      # Top 50 Brasil
    "US": "4NYOtcP8uR78vxFscJtOhU",      # Top 50 USA
    "MX": "1QGHb6CaUuA6pf6Z5DYDUM",      # Top 50 México
    "PT": "0iXCcDOlT2OeRzbOujXdGH"       # Top 50 Portugal
}

def extract_spotify_tracks():
    all_data = []
    for region, playlist_id in REGIONS.items():
        print(f"🎶 Extraindo playlist {region}...")
        results = sp.playlist_tracks(playlist_id, additional_types=["track"])
        for item in results["items"]:
            track = item["track"]
            if not track:
                continue
            all_data.append({
                "track_id": track["id"],
                "track_name": track["name"],
                "artist_name": ", ".join([a["name"] for a in track["artists"]]),
                "album_name": track["album"]["name"],
                "release_year": int(track["album"]["release_date"][:4]),
                "duration_s": track["duration_ms"] // 1000,
                "popularity": track["popularity"],
                "region": region
            })
    return pd.DataFrame(all_data)

if __name__ == "__main__":
    df = extract_spotify_tracks()
    print(df.groupby("region")["track_id"].count())
    df.to_csv("spotify_tracks.csv", index=False, encoding="utf-8")
