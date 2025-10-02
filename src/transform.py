import pandas as pd
from rapidfuzz import fuzz

def correlate_music_video(spotify_df: pd.DataFrame, youtube_df: pd.DataFrame, threshold: int = 85) -> pd.DataFrame:
    """
    Cria correlações entre faixas do Spotify e vídeos do YouTube
    com base em similaridade de nomes (fuzzy matching).
    
    Args:
        spotify_df: DataFrame de faixas do Spotify
        youtube_df: DataFrame de vídeos do YouTube
        threshold: nível mínimo de similaridade (0-100)

    Returns:
        DataFrame com as correlações encontradas
    """
    results = []
    if spotify_df.empty or youtube_df.empty:
        return pd.DataFrame()

    for _, s_row in spotify_df.iterrows():
        track_name = f"{s_row['track_name']} {s_row['artist_name']}"
        best_match = None
        best_score = 0
        matched_video = None

        for _, y_row in youtube_df.iterrows():
            video_title = y_row["title"]
            score = fuzz.token_set_ratio(track_name, video_title)

            if score > best_score:
                best_score = score
                best_match = video_title
                matched_video = y_row

        if best_score >= threshold and matched_video is not None:
            results.append({
                "track_id": s_row["track_id"],
                "track_name": s_row["track_name"],
                "artist_name": s_row["artist_name"],
                "video_id": matched_video["video_id"],
                "video_title": best_match,
                "similarity_score": best_score,
                "region_spotify": s_row.get("region", "N/A"),
                "region_youtube": matched_video.get("region", "N/A")
            })

    return pd.DataFrame(results)
