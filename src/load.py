import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def load_table(file, table_name, if_exists="replace"):
    df = pd.read_csv(file)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"Tabela `{table_name}` carregada com {len(df)} registros.")

if __name__ == "__main__":
    load_table("spotify_tracks.csv", "spotify_tracks", if_exists="replace")
    load_table("youtube_videos.csv", "youtube_videos", if_exists="replace")
