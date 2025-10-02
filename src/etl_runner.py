# src/etl_runner.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from extract_spotify import get_spotify_client, fetch_playlist_tracks
from extract_youtube import get_youtube_client, fetch_most_popular_videos
from transform import normalize_spotify, normalize_youtube, correlate_music_video
from load import load_dataframe

# --- Conexão com o banco ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- Criação das tabelas ---
init_sql = """
CREATE TABLE IF NOT EXISTS spotify_tracks (
    track_id TEXT PRIMARY KEY,
    name TEXT,
    artist TEXT,
    album TEXT,
    release_date DATE,
    popularity INT,
    duration_ms INT,
    explicit BOOLEAN,
    danceability FLOAT,
    energy FLOAT,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS youtube_videos (
    video_id TEXT PRIMARY KEY,
    title TEXT,
    channel_title TEXT,
    category_id TEXT,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    published_at TIMESTAMP,
    description TEXT,
    region TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS correlations (
    id SERIAL PRIMARY KEY,
    track_id TEXT REFERENCES spotify_tracks(track_id),
    video_id TEXT REFERENCES youtube_videos(video_id),
    similarity_score FLOAT,
    reason TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

with engine.begin() as conn:
    conn.execute(text(init_sql))
    print("✅ Tabelas criadas/verificadas com sucesso!")


# --- Pipeline ETL ---
def run():
    sp = get_spotify_client()
    yt = get_youtube_client()

    # Extract Spotify (usei sua playlist em vez da Global)
    spotify_df = fetch_playlist_tracks(sp, playlist_id="2Y1AD7uedwsVvCrLYQmqTI", limit=100)

    # Extract YouTube de várias regiões
    regions = ["BR", "US", "MX", "PT"]
    youtube_dfs = []
    for region in regions:
        df = fetch_most_popular_videos(yt, regionCode=region, maxResults=50)
        df["region"] = region
        youtube_dfs.append(df)
    youtube_df = pd.concat(youtube_dfs, ignore_index=True)

    # Transform
    spotify_norm = normalize_spotify(spotify_df)
    youtube_norm = normalize_youtube(youtube_df)

    # Load
    load_dataframe(spotify_norm, "spotify_tracks", if_exists="append")
    load_dataframe(youtube_norm, "youtube_videos", if_exists="append")

    # Correlate
    corr_df = correlate_music_video(spotify_norm, youtube_norm)
    if not corr_df.empty:
        load_dataframe(corr_df, "correlations", if_exists="append")

    print("✅ ETL finalizado com sucesso!")


if __name__ == "__main__":
    run()
