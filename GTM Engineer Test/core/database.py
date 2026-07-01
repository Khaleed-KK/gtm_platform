import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# FALLBACK GUARD: If os.getenv fails to find the key or evaluates to None, fall back to the string literal.
raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    DB_URL = "postgresql://neondb_owner:npg_DJUayd9lxkC2@ep-delicate-sound-aog52z2w-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
else:
    DB_URL = raw_url

def get_db_connection():
    """Reusable connection factory for the entire app."""
    return psycopg.connect(DB_URL, autocommit=True)

def init_database():
    """Resets and prepares the database structure with optimized indexing."""
    schema_sql = """
    DROP TABLE IF EXISTS video_metrics CASCADE;
    DROP TABLE IF EXISTS videos CASCADE;
    DROP TABLE IF EXISTS recommendations CASCADE;

    CREATE TABLE videos (
        video_id VARCHAR(50) PRIMARY KEY,
        channel_title VARCHAR(100) NOT NULL,
        title TEXT NOT NULL,
        published_at TIMESTAMP NOT NULL,
        topic VARCHAR(100),
        format VARCHAR(100)
    );

    CREATE TABLE video_metrics (
        id SERIAL PRIMARY KEY,
        video_id VARCHAR(50) REFERENCES videos(video_id) ON DELETE CASCADE,
        captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        view_count INT NOT NULL,
        like_count INT NOT NULL,
        comment_count INT NOT NULL
    );

    CREATE TABLE recommendations (
        id SERIAL PRIMARY KEY,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        topic VARCHAR(100) NOT NULL,
        format VARCHAR(100) NOT NULL,
        angle TEXT NOT NULL,
        reasoning TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_video_metrics_video_id ON video_metrics(video_id);
    CREATE INDEX IF NOT EXISTS idx_video_metrics_captured_at ON video_metrics(captured_at);
    """
    print("Initializing pristine schema on Neon Postgres...")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            print("Core tables successfully deployed with indexes.")

if __name__ == "__main__":
    init_database()