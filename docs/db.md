# Database

## Database Schema

### Table: `keywords`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `keyword`: TEXT NOT NULL - The keyword or search term
- `rank`: INTEGER NOT NULL - Ranking position 
- `score`: INTEGER NOT NULL - Relevance score (e.g. search volume, view count)
- `platform`: TEXT NOT NULL - Source platform (e.g. 'youtube', 'twitter')
- `region`: TEXT NOT NULL - Region code (e.g. 'TW', 'US')
- `metadata`: JSON - Additional platform-specific data
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP



### Table: `transcripts`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `video_id`: INTEGER NOT NULL - References videos.id
- `transcript`: TEXT NOT NULL - Transcribed text
- `language`: TEXT NOT NULL - Language of the transcript
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

### Table: `videos`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `keyword_id`: INTEGER NOT NULL - References keywords.id
- `video_category`: TEXT NOT NULL - Category of the video
- `video_thumbnail_url`: TEXT NOT NULL - URL of the video thumbnail
- `video_url`: TEXT NOT NULL - URL of the video
- `video_title`: TEXT NOT NULL - Title of the video
- `video_youtube_id`: TEXT NOT NULL - ID of the video in youtube
- `video_duration`: INTEGER NOT NULL - Duration of the video in seconds
- `video_views`: INTEGER NOT NULL - Number of views of the video
- `video_likes`: INTEGER NOT NULL - Number of likes of the video
- `video_language`: TEXT NOT NULL - Language of the video
- `video_comments`: INTEGER NOT NULL - Number of comments of the video
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

### Table: `articles`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `keyword_id`: INTEGER NOT NULL - References keywords.id
- `transcript_id`: INTEGER NOT NULL - References transcripts.id
- `video_id`: INTEGER NOT NULL - References videos.id
- `article_language`: TEXT NOT NULL - Language of the article
- `title`: TEXT NOT NULL - Title of the article
- `content`: TEXT NOT NULL - Content of the article
- `tags`: TEXT NOT NULL - Tags of the article
- `seo_metadata`: JSON - SEO metadata of the article
- `published`: BOOLEAN NOT NULL DEFAULT FALSE - Whether the article is published
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP