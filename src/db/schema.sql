CREATE TABLE IF NOT EXISTS spotify_tracks (
  track_id TEXT PRIMARY KEY,
  name TEXT,
  artist TEXT,
  artists JSONB,
  album TEXT,
  popularity INTEGER,
  duration_ms INTEGER,
  release_date DATE,
  fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS youtube_videos (
  video_id TEXT PRIMARY KEY,
  title TEXT,
  channel_title TEXT,
  category_id TEXT,
  view_count BIGINT,
  like_count BIGINT,
  comment_count BIGINT,
  published_at TIMESTAMP,
  description TEXT,
  fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS correlations (
  id SERIAL PRIMARY KEY,
  track_id TEXT,
  video_id TEXT,
  similarity_score NUMERIC,
  reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
