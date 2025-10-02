# src/transform.py
import pandas as pd
import json
from datetime import datetime
from rapidfuzz import fuzz

def normalize_spotify(df):
    df = df.copy()
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['artists'] = df['artists'].apply(lambda x: json.dumps(x) if isinstance(x, list) else json.dumps([]))
    df['fetched_at'] = datetime.utcnow()
    return df

def normalize_youtube(df):
    df = df.copy()
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    # garantir coluna region (se foi buscado sem region, preencher 'UNKNOWN')
    if 'region' not in df.columns:
        df['region'] = 'UNKNOWN'
    df['fetched_at'] = datetime.utcnow()
    return df

def correlate_music_video(spotify_df, youtube_df):
    rows = []
    for _, track in spotify_df.iterrows():
        for _, video in youtube_df.iterrows():
            score = fuzz.partial_ratio(track['name'].lower(), str(video['title']).lower())
            if score >= 80:
                rows.append({
                    'track_id': track['track_id'],
                    'video_id': video['video_id'],
                    'similarity_score': score,
                    'reason': f"name_match:{score}"
                })
    return pd.DataFrame(rows)
