import os
import sys
from googleapiclient.discovery import build

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import get_db_connection
from pipeline.ai_engine import generate_ai_gtm_recommendation


def resolve_channel_id(youtube, handle_or_id):
    """Resolves a public custom handle (e.g., @HubSpot-CRM) to a strict system-level Channel ID."""
    if handle_or_id.startswith("UC"):
        return handle_or_id

    clean_handle = handle_or_id if handle_or_id.startswith("@") else f"@{handle_or_id}"

    print(f"🛰️ [1/4] Connecting to YouTube API to resolve handle: {clean_handle}...")
    response = youtube.channels().list(
        part="id",
        forHandle=clean_handle
    ).execute()

    items = response.get("items", [])
    if not items:
        raise ValueError(f"Could not resolve official channel ID for handle: {clean_handle}")
    return items[0]["id"]


def categorize_video(title):
    title_lower = title.lower()
    topic = "AI & Automation" if any(
        x in title_lower for x in ["ai", "chatgpt", "llm", "claude", "gemini"]) else "GTM Strategy"
    video_format = "Product Tutorial" if any(
        x in title_lower for x in ["how", "guide", "tutorial"]) else "Founder Case Study"
    return topic, video_format


def run_pipeline(target_identifier="@HubSpot-CRM"):
    """Queries recent channel assets, performs metadata checks, and logs time-series snapshots."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        # Step 1: Handle resolution
        channel_id = resolve_channel_id(youtube, target_identifier)

        # Step 2: Fetch video list
        print("🔍 [2/4] Fetching newest 5 videos from the upload feed...")
        search_response = youtube.search().list(
            channelId=channel_id, part="snippet", type="video", maxResults=5, order="date"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            print("⚠️ No videos discovered for the target profile.")
            return None

        # Step 3: Fetch video metrics
        print(f"📈 [3/4] Hydrating view/like/comment metrics for video IDs: {video_ids}")
        video_response = youtube.videos().list(
            part="snippet,statistics", id=",".join(video_ids)
        ).execute()
        raw_videos = video_response.get("items", [])

        ai_payload = []

        # Step 4: Database Connection and Commit
        print("🐘 [4/4] Opening connection to Neon PostgreSQL database...")
        with get_db_connection() as conn:
            print("🔗 Database connection established successfully. Executing SQL transactions...")
            with conn.cursor() as cursor:
                for video in raw_videos:
                    v_id = video["id"]
                    title = video["snippet"]["title"]
                    channel_title = video["snippet"]["channelTitle"]
                    pub_at = video["snippet"]["publishedAt"]
                    views = int(video["statistics"].get("viewCount", 0))

                    topic, video_format = categorize_video(title)
                    ai_payload.append(
                        {"title": title, "channel": channel_title, "views": views, "format": video_format})

                    cursor.execute("""
                        INSERT INTO videos (video_id, channel_title, title, published_at, topic, format)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (video_id) DO UPDATE SET title = EXCLUDED.title;
                    """, (v_id, channel_title, title, pub_at, topic, video_format))

                    cursor.execute("""
                        INSERT INTO video_metrics_snapshots (video_id, view_count, like_count, comment_count)
                        VALUES (%s, %s, %s, %s);
                    """, (v_id, views, int(video["statistics"].get("likeCount", 0)),
                          int(video["statistics"].get("commentCount", 0))))

        print("🧠 Routing data payload to Gemini Intelligence Engine...")
        generate_ai_gtm_recommendation(channel_title, ai_payload)
        return channel_title
    except Exception as e:
        print(f"❌ Pipeline running error: {e}")
        return None