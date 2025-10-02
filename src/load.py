import os
import pandas as pd
from sqlalchemy import create_engine, MetaData
from dotenv import load_dotenv

load_dotenv()

# Lê variáveis do .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Monta a URL do banco (🔧 força UTF-8)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

# Cria engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

def load_dataframe(df, table_name, if_exists="append", index=False):
    """
    Carrega DataFrame para o PostgreSQL.
    - Converte 'artists' para JSON string (quando existir)
    - Ignora duplicatas usando if_exists='append'
    """
    if "artists" in df.columns:
        df["artists"] = df["artists"].apply(lambda x: x if isinstance(x, str) else str(x))

    try:
        df.to_sql(table_name, engine, if_exists=if_exists, index=index)
        print(f"[load_dataframe] Inserido {len(df)} linhas em {table_name}.")
    except Exception as e:
        print(f"[load_dataframe] Erro ao inserir em {table_name}: {e}")

def load_categories_mapping(df):
    """
    Carrega o mapeamento de categorias do YouTube.
    """
    try:
        df.to_sql("youtube_categories", engine, if_exists="append", index=False)
        print(f"[load_categories_mapping] Inserido {len(df)} categorias no banco.")
    except Exception as e:
        print(f"[load_categories_mapping] Erro ao inserir categorias: {e}")
