import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Importar funções do projeto
from extract_spotify import extract_spotify_tracks
from extract_youtube import extract_youtube_videos
from transform import correlate_music_video

# ========================
# Configuração
# ========================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ========================
# Testes
# ========================

def test_spotify_extraction():
    df = extract_spotify_tracks()
    assert not df.empty, "❌ Nenhum dado extraído do Spotify"
    assert "track_name" in df.columns, "❌ Coluna track_name não encontrada"
    assert df["popularity"].between(0, 100).all(), "❌ Popularidade fora da faixa (0-100)"
    assert df["duration_s"].gt(0).all(), "❌ Faixa com duração inválida"
    print("✅ Teste Spotify passou")

def test_youtube_extraction():
    df = extract_youtube_videos()
    assert not df.empty, "❌ Nenhum dado extraído do YouTube"
    assert "title" in df.columns, "❌ Coluna title não encontrada"
    assert df["view_count"].ge(0).all(), "❌ Views inválidos encontrados"
    print("✅ Teste YouTube passou")

def test_correlation():
    sp = extract_spotify_tracks()
    yt = extract_youtube_videos()
    corr = correlate_music_video(sp, yt, threshold=80)

    expected_cols = [
        "track_name",
        "artist_name",
        "video_title",
        "similarity_score"  # ✅ coluna correta
    ]
    for col in expected_cols:
        assert col in corr.columns, f"❌ Coluna {col} ausente na correlação"
    assert corr["similarity_score"].between(0, 100).all(), "❌ Similaridade fora da faixa (0-100)"
    print("✅ Teste Correlação passou")

def test_database_load():
    with engine.connect() as conn:
        tables = ["spotify_tracks", "youtube_videos", "correlations"]
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            assert count > 0, f"❌ Tabela {table} está vazia"
            print(f"✅ Tabela {table} carregada com {count} registros")

# ========================
# Runner
# ========================

def run_all_tests():
    print("🚀 Iniciando testes...\n")
    test_spotify_extraction()
    test_youtube_extraction()
    test_correlation()
    test_database_load()
    print("\n🎉 Todos os testes passaram com sucesso!")

if __name__ == "__main__":
    run_all_tests()
