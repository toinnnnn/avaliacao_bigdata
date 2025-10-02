# src/app_streamlit.py
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
from rapidfuzz import process

# ================================
# Configuração
# ================================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_youtube")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ================================
# Funções auxiliares
# ================================
@st.cache_data
def load_spotify():
    return pd.read_sql("SELECT * FROM spotify_tracks", engine)

@st.cache_data
def load_youtube():
    return pd.read_sql("SELECT * FROM youtube_videos", engine)

# ================================
# Carregar dados
# ================================
spotify_df = load_spotify()
youtube_df = load_youtube()

# ================================
# Layout inicial
# ================================
st.set_page_config(page_title="Dashboard Spotify & YouTube", layout="wide", initial_sidebar_state="expanded")
st.sidebar.header("🎚️ Filtros")

# ================================
# Filtros globais
# ================================
# Região
regions = sorted(list(set(spotify_df['region'].unique()) | set(youtube_df['region'].unique())))
region_sel = st.sidebar.multiselect("🌍 Regiões", regions, default=regions)

# Ano (Spotify)
years = sorted(spotify_df['release_year'].dropna().unique())
if years:
    year_sel = st.sidebar.slider("📅 Intervalo de Anos", int(min(years)), int(max(years)),
                                 (int(min(years)), int(max(years))))
else:
    year_sel = (2000, 2025)

# Spotify - artistas
artists = sorted(spotify_df['artist_name'].dropna().unique())
artist_sel = st.sidebar.multiselect("👤 Artistas (Spotify)", artists, default=artists)

# Spotify - popularidade
pop_min, pop_max = int(spotify_df['popularity'].min()), int(spotify_df['popularity'].max())
popularity_sel = st.sidebar.slider("🔥 Popularidade (Spotify)", pop_min, pop_max, (pop_min, pop_max))

# YouTube - categorias
categories = sorted(youtube_df['category'].dropna().unique())
category_sel = st.sidebar.multiselect("🎬 Categorias (YouTube)", categories, default=categories)

# YouTube - canais
channels = sorted(youtube_df['channel_title'].dropna().unique())
channel_sel = st.sidebar.multiselect("📺 Canais (YouTube)", channels, default=channels)

# YouTube - engajamento
views_min, views_max = int(youtube_df['view_count'].min()), int(youtube_df['view_count'].max())
views_sel = st.sidebar.slider("👀 Views (YouTube)", views_min, views_max, (views_min, views_max))

# ================================
# Aplicar filtros
# ================================
spotify_df = spotify_df[
    (spotify_df['region'].isin(region_sel)) &
    (spotify_df['release_year'].between(year_sel[0], year_sel[1])) &
    (spotify_df['artist_name'].isin(artist_sel)) &
    (spotify_df['popularity'].between(popularity_sel[0], popularity_sel[1]))
]

youtube_df = youtube_df[
    (youtube_df['region'].isin(region_sel)) &
    (youtube_df['category'].isin(category_sel)) &
    (youtube_df['channel_title'].isin(channel_sel)) &
    (youtube_df['view_count'].between(views_sel[0], views_sel[1]))
]

# ================================
# Layout principal
# ================================
st.title("📊 Dashboard Spotify & YouTube")
st.markdown("Exploração interativa dos dados de músicas e vídeos com base nos ETLs desenvolvidos.")

# ================================
# 1. Análise Spotify
# ================================
st.header("🎵 Spotify - Faixas e Popularidade")

col1, col2 = st.columns(2)
with col1:
    if not spotify_df.empty:
        fig = px.histogram(spotify_df, x="popularity", nbins=20, title="Distribuição da Popularidade")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Nenhum dado após aplicar os filtros.")

with col2:
    if not spotify_df.empty:
        fig = px.histogram(spotify_df, x="duration_s", nbins=20, title="Distribuição da Duração (s)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Nenhum dado após aplicar os filtros.")

# ================================
# 2. YouTube - Visão geral
# ================================
st.header("📺 YouTube - Visão Geral")

if not youtube_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vídeos", youtube_df['video_id'].nunique())
    col2.metric("Canais únicos", youtube_df['channel_id'].nunique())
    col3.metric("Views total", f"{youtube_df['view_count'].sum():,}")
    col4.metric("Comentários total", f"{youtube_df['comment_count'].sum():,}")
else:
    st.info("⚠️ Nenhum dado de YouTube após aplicar os filtros.")

# ================================
# 3. Categorias YouTube
# ================================
st.subheader("🎬 Top Categorias por Views")

if not youtube_df.empty:
    cat_df = youtube_df.groupby("category", as_index=False)['view_count'].sum()
    cat_df = cat_df.sort_values(by="view_count", ascending=False).head(10)

    fig = px.bar(cat_df, x="category", y="view_count", title="Top Categorias (Views)", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("⚠️ Nenhum dado de categoria após aplicar os filtros.")

# ================================
# 4. Engajamento por Região
# ================================
st.header("🌍 Análise por Região")

col1, col2 = st.columns(2)
with col1:
    region_sp = spotify_df.groupby("region", as_index=False)['popularity'].mean()
    if not region_sp.empty:
        fig = px.bar(region_sp, x="region", y="popularity", title="Popularidade Média no Spotify", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Nenhum dado Spotify após aplicar os filtros.")

with col2:
    region_yt = youtube_df.groupby("region", as_index=False)['view_count'].sum()
    if not region_yt.empty:
        fig = px.bar(region_yt, x="region", y="view_count", title="Views Totais no YouTube", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Nenhum dado YouTube após aplicar os filtros.")

# ================================
# 5. Correlação Spotify x YouTube
# ================================
st.header("🔗 Correlação Spotify x YouTube")

corr_data = []
yt_titles = youtube_df['title'].dropna().unique().tolist()

for _, row in spotify_df.iterrows():
    match = process.extractOne(row['track_name'], yt_titles, score_cutoff=80)
    if match:
        yt_row = youtube_df[youtube_df['title'] == match[0]].iloc[0]
        corr_data.append({
            "track_name": row['track_name'],
            "artist_name": row['artist_name'],
            "popularity": row['popularity'],
            "video_title": yt_row['title'],
            "view_count": yt_row['view_count'],
            "score": match[1]
        })

corr_df = pd.DataFrame(corr_data)
if not corr_df.empty:
    fig = px.scatter(
        corr_df, x="popularity", y="view_count",
        hover_data=["track_name", "artist_name", "video_title", "score"],
        title="Popularidade (Spotify) vs Views (YouTube)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("⚠️ Nenhuma correspondência encontrada após aplicar os filtros.")

# ================================
# Rodapé
# ================================
st.markdown("---")
st.caption("Dashboard criado para a atividade. Use Ctrl+C no terminal para parar o Streamlit.")
