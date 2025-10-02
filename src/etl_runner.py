import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

from extract_spotify import extract_spotify_tracks
from extract_youtube import extract_youtube_videos
from transform import correlate_music_video  # já implementa as similaridades

load_dotenv()

# Conexão com PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def safe_to_sql(df: pd.DataFrame, table_name: str):
    if df.empty:
        print(f"⚠️ Nenhum dado para {table_name}, ignorando.")
        return
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"✅ Tabela {table_name} carregada com {len(df)} registros.")

def run():
    # ======================
    # Spotify
    # ======================
    print("🎵 Extraindo Spotify...")
    spotify_df = extract_spotify_tracks()
    safe_to_sql(spotify_df, "spotify_tracks")

    # ======================
    # YouTube
    # ======================
    print("📺 Extraindo YouTube...")
    youtube_df = extract_youtube_videos()
    safe_to_sql(youtube_df, "youtube_videos")

    # ======================
    # Correlação
    # ======================
    print("🔗 Calculando correlações...")
    corr_df = correlate_music_video(spotify_df, youtube_df, threshold=85)
    safe_to_sql(corr_df, "correlations")

    print("🚀 ETL finalizado com sucesso!")

if __name__ == "__main__":
    run()
