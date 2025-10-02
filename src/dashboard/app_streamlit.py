# src/dashboard/app_streamlit.py

import os
import urllib.parse
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# -----------------------------
# Config / .env
# -----------------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DB_PASSWORD_SAFE = urllib.parse.quote_plus(DB_PASSWORD)

# Force client encoding option (we also execute SET client_encoding at runtime)
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD_SAFE}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"options": "-c client_encoding=UTF8"}
)

# -----------------------------
# Helper: carregar tabela
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data(table_name: str) -> pd.DataFrame:
    """
    Tenta carregar a tabela. Faz SET client_encoding TO 'UTF8' antes do SELECT.
    Em caso de erro, captura e retorna DataFrame vazio (e a UI exibirá mensagem).
    """
    try:
        with engine.connect() as conn:
            # usar sqlalchemy.text para evitar "Not an executable object"
            conn.execute(text("SET client_encoding TO 'UTF8'"))
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        # devolve DataFrame vazio e propaga mensagem via retorno conveniente
        raise RuntimeError(f"Erro ao ler tabela {table_name}: {e}") from e

# -----------------------------
# Streamlit layout
# -----------------------------
st.set_page_config(page_title="🎶 Spotify & YouTube Dashboard", layout="wide")

# Sidebar / Navegação
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1384/1384060.png", width=96)
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Dashboard", "Spotify", "YouTube", "Correlação", "Regiões"])

# Header
st.markdown(
    "<h1 style='text-align: center; color: #1DB954; margin-bottom: 0.1rem;'>🎶 Spotify & YouTube Analytics</h1>",
    unsafe_allow_html=True,
)
st.markdown("<div style='text-align:center; color: #666;'>Análise e correlação entre dados do Spotify e do YouTube</div>", unsafe_allow_html=True)
st.markdown("---")

# Carregar dados (com mensagens de erro amigáveis)
spotify_df = pd.DataFrame()
youtube_df = pd.DataFrame()
correlations_df = pd.DataFrame()

try:
    spotify_df = load_data("spotify_tracks")
except Exception as e:
    st.sidebar.error(str(e))

try:
    youtube_df = load_data("youtube_videos")
except Exception as e:
    st.sidebar.error(str(e))

try:
    correlations_df = load_data("correlations")
except Exception as e:
    st.sidebar.error(str(e))

# -----------------------------
# Função utilitária: cards de métricas
# -----------------------------
def show_summary_cards_for_spotify(df: pd.DataFrame):
    c1, c2, c3, c4 = st.columns(4)
    if not df.empty:
        c1.metric("Músicas (linhas)", f"{len(df):,}")
        c2.metric("Artistas únicos", f"{df['artist'].nunique():,}" if "artist" in df.columns else "—")
        if "popularity" in df.columns:
            c3.metric("Popularidade média", f"{df['popularity'].mean():.1f}")
        else:
            c3.metric("Popularidade média", "—")
        if "duration_ms" in df.columns:
            c4.metric("Duração média (s)", f"{(df['duration_ms'].mean() / 1000):.0f}")
        else:
            c4.metric("Duração média (s)", "—")
    else:
        c1.info("Sem dados")
        c2.info("")
        c3.info("")
        c4.info("")

def show_summary_cards_for_youtube(df: pd.DataFrame):
    c1, c2, c3, c4 = st.columns(4)
    if not df.empty:
        c1.metric("Vídeos (linhas)", f"{len(df):,}")
        c2.metric("Canais únicos", f"{df['channel_title'].nunique():,}" if "channel_title" in df.columns else "—")
        c3.metric("Views total", f"{df['view_count'].sum():,}" if "view_count" in df.columns else "—")
        c4.metric("Comentários total", f"{df['comment_count'].sum():,}" if "comment_count" in df.columns else "—")
    else:
        c1.info("Sem dados")
        c2.info("")
        c3.info("")
        c4.info("")

# -----------------------------
# Pages
# -----------------------------
if page == "Dashboard":
    st.subheader("Visão geral")
    st.markdown("Resumo rápido das três fontes de dados.")
    st.markdown("**Spotify**")
    show_summary_cards_for_spotify(spotify_df)
    st.markdown("**YouTube**")
    show_summary_cards_for_youtube(youtube_df)
    st.markdown("**Correlações**")
    if not correlations_df.empty:
        st.write(f"Total de correlações: **{len(correlations_df):,}**")
    else:
        st.info("Nenhuma correlação carregada.")

elif page == "Spotify":
    st.subheader("📈 Spotify - dados e gráficos")
    if spotify_df.empty:
        st.warning("Nenhum dado do Spotify disponível.")
    else:
        show_summary_cards_for_spotify(spotify_df)
        st.markdown("**Top 20 artistas por popularidade média**")
        top_artists = (
            spotify_df.groupby("artist")["popularity"].mean().reset_index().sort_values("popularity", ascending=False).head(20)
        )
        fig = px.bar(top_artists, x="artist", y="popularity", text="popularity",
                     title="Top 20 Artistas (Popularidade média)",
                     color="popularity", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Tabela (amostra)**")
        st.dataframe(spotify_df.head(200))

elif page == "YouTube":
    st.subheader("📺 YouTube - dados e gráficos")
    if youtube_df.empty:
        st.warning("Nenhum dado do YouTube disponível.")
    else:
        show_summary_cards_for_youtube(youtube_df)

        st.markdown("**Top categorias (por views)**")
        if "category_id" in youtube_df.columns and "view_count" in youtube_df.columns:
            top_cats = youtube_df.groupby("category_id")["view_count"].sum().reset_index().sort_values("view_count", ascending=False).head(10)
            fig = px.pie(top_cats, names="category_id", values="view_count", title="Distribuição de Views por Categoria (Top 10)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top_cats)
        else:
            st.info("category_id ou view_count não disponível.")

        st.markdown("**Views vs Likes (tamanho = comentários)**")
        if {"view_count", "like_count", "comment_count"}.issubset(youtube_df.columns):
            fig2 = px.scatter(youtube_df, x="view_count", y="like_count", size="comment_count", hover_name="title",
                              title="Views vs Likes (tamanho = comentários)")
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("**Tabela (amostra)**")
        st.dataframe(youtube_df.head(200))

elif page == "Correlação":
    st.subheader("🔗 Correlações encontradas")
    if correlations_df.empty:
        st.warning("Nenhuma correlação carregada.")
    else:
        st.markdown("**Resumo e tabela**")
        st.dataframe(correlations_df.sort_values("similarity_score", ascending=False).head(200))
        st.markdown("**Distribuição de scores de similaridade**")
        if "similarity_score" in correlations_df.columns:
            fig = px.histogram(correlations_df, x="similarity_score", nbins=20, title="Distribuição de similarity_score")
            st.plotly_chart(fig, use_container_width=True)
        # gráfico comparativo: popularidade da música vs views do vídeo (se possível)
        if {"track_id", "video_id"}.issubset(correlations_df.columns) and not spotify_df.empty and not youtube_df.empty:
            # juntar dados (inner join simples)
            join_df = correlations_df.merge(spotify_df[["track_id", "popularity"]], on="track_id", how="left") \
                                     .merge(youtube_df[["video_id", "view_count"]], on="video_id", how="left")
            if {"popularity", "view_count"}.issubset(join_df.columns):
                st.markdown("**Popularidade (Spotify) vs Views (YouTube) — correlações encontradas**")
                fig2 = px.scatter(join_df, x="popularity", y="view_count", hover_data=["track_id", "video_id"],
                                  title="Popularidade (Spotify) vs Views (YouTube)")
                st.plotly_chart(fig2, use_container_width=True)

elif page == "Regiões":
    st.subheader("🌍 Análise por Região (YouTube)")
    if youtube_df.empty:
        st.warning("Nenhum dado do YouTube disponível.")
    else:
        if "region" in youtube_df.columns and "view_count" in youtube_df.columns:
            region_views = youtube_df.groupby("region")["view_count"].sum().reset_index().sort_values("view_count", ascending=False)
            fig = px.bar(region_views, x="region", y="view_count", text="view_count", title="Views por Região")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(region_views)
        else:
            st.info("As colunas 'region' e 'view_count' são necessárias para esta aba.")

# Footer / nota
st.markdown("---")
st.caption("Dashboard criado para a atividade. (Use Ctrl+C no terminal para parar o Streamlit)")
