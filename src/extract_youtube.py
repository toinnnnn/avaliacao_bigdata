import pandas as pd

def get_youtube_client():
    from googleapiclient.discovery import build
    import os
    api_key = os.getenv("YOUTUBE_API_KEY")
    return build("youtube", "v3", developerKey=api_key)


def fetch_most_popular_videos(youtube, regionCode='BR', maxResults=50):
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=regionCode,
        maxResults=maxResults
    )
    response = request.execute()

    rows = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        rows.append({
            "video_id": item["id"],
            "title": snippet.get("title"),
            "channel_title": snippet.get("channelTitle"),
            "category_id": snippet.get("categoryId"),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "published_at": snippet.get("publishedAt"),
            "description": snippet.get("description"),
            "region": regionCode  # <<< adicionamos aqui
        })

    return pd.DataFrame(rows)
