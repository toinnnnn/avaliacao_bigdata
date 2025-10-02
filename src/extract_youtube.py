import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Autenticação
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Regiões que vamos capturar
REGIONS = ["BR", "US", "MX", "PT"]

# Mapeamento Category ID → Nome real
YOUTUBE_CATEGORIES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology"
}

def extract_youtube_videos():
    all_data = []
    for region in REGIONS:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region,
            maxResults=50
        )
        response = request.execute()

        for item in response["items"]:
            stats = item["statistics"]
            cat_id = str(item["snippet"].get("categoryId", ""))
            cat_name = YOUTUBE_CATEGORIES.get(cat_id, cat_id)

            all_data.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "channel_id": item["snippet"]["channelId"],
                "channel_title": item["snippet"]["channelTitle"],
                "category": cat_name,  # 🔥 já salva com nome legível
                "published_at": item["snippet"]["publishedAt"],
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "region": region
            })
    return pd.DataFrame(all_data)

if __name__ == "__main__":
    df = extract_youtube_videos()
    print(df.head())
    df.to_csv("youtube_videos.csv", index=False, encoding="utf-8")
