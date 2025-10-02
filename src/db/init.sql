-- Criação da tabela de músicas do Spotify
CREATE TABLE IF NOT EXISTS spotify_tracks (
    id SERIAL PRIMARY KEY,
    track_id TEXT NOT NULL,
    name TEXT,
    artist TEXT,
    album TEXT,
    popularity INT,
    duration_ms INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criação da tabela de vídeos do YouTube
CREATE TABLE IF NOT EXISTS youtube_videos (
    id SERIAL PRIMARY KEY,
    video_id TEXT NOT NULL,
    title TEXT,
    channel_title TEXT,
    category_id INT,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    region TEXT,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criação da tabela de correlações entre músicas e vídeos
CREATE TABLE IF NOT EXISTS correlations (
    id SERIAL PRIMARY KEY,
    track_id TEXT NOT NULL,
    video_id TEXT NOT NULL,
    similarity_score FLOAT,
    reason TEXT,
    correlated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
