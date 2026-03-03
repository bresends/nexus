import sys
import os
import time
import requests
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database.database import SessionLocal
from src.models.video_log import VideoLog


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from a full URL."""
    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
        return video_id if video_id else None

    path = parsed.path
    for prefix in ("/shorts/", "/live/"):
        if path.startswith(prefix):
            return path[len(prefix):].split("/")[0].split("?")[0]

    v = parse_qs(parsed.query).get("v")
    if v:
        return v[0]

    return None


def step1_extract_video_ids(db):
    """Find rows where video_id is a URL and extract the actual ID."""
    print("=== Step 1: Extract video IDs from URLs ===\n")

    url_rows = db.query(VideoLog).filter(
        (VideoLog.video_id.like("%youtube.com%")) |
        (VideoLog.video_id.like("%youtu.be%"))
    ).all()

    print(f"Found {len(url_rows)} rows with URLs in video_id\n")

    fixed = 0
    deleted = 0
    failed = 0
    total = len(url_rows)

    for i, row in enumerate(url_rows):
        remaining = total - i - 1
        video_id = extract_video_id(row.video_id)

        if not video_id:
            print(f"  [{i+1}/{total}] SKIP id={row.id}: could not extract ID from '{row.video_id}' ({remaining} left)")
            failed += 1
            continue

        existing = db.query(VideoLog).filter(
            VideoLog.video_id == video_id,
            VideoLog.id != row.id,
        ).first()

        if existing:
            print(f"  [{i+1}/{total}] DELETE id={row.id}: '{row.video_id}' -> '{video_id}' (duplicate of id={existing.id}) ({remaining} left)")
            db.delete(row)
            deleted += 1
        else:
            print(f"  [{i+1}/{total}] UPDATE id={row.id}: '{row.video_id}' -> '{video_id}' ({remaining} left)")
            row.video_id = video_id
            fixed += 1

        db.commit()
    print(f"\nStep 1 done. Fixed: {fixed}, Deleted duplicates: {deleted}, Failed: {failed}\n")


def step2_backfill_channel_info(db):
    """Fetch channel info from YouTube oEmbed for rows missing it."""
    print("=== Step 2: Backfill channel info ===\n")

    rows = db.query(VideoLog).filter(
        (VideoLog.channel_name.is_(None)) | (VideoLog.channel_url.is_(None))
    ).all()

    print(f"Found {len(rows)} rows missing channel info\n")

    updated = 0
    failed = 0
    total = len(rows)

    for i, row in enumerate(rows):
        remaining = total - i - 1
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={row.video_id}&format=json"

        try:
            resp = requests.get(url, timeout=10)
            if not resp.ok:
                print(f"  [{i+1}/{total}] FAIL id={row.id} video_id={row.video_id}: HTTP {resp.status_code} ({remaining} left)")
                failed += 1
                continue

            data = resp.json()
            row.channel_name = data.get("author_name")
            row.channel_url = data.get("author_url")
            print(f"  [{i+1}/{total}] OK id={row.id} video_id={row.video_id}: {row.channel_name} ({remaining} left)")
            updated += 1
            db.commit()

        except Exception as e:
            print(f"  [{i+1}/{total}] ERROR id={row.id} video_id={row.video_id}: {e} ({remaining} left)")
            failed += 1

        time.sleep(0.5)

    print(f"\nStep 2 done. Updated: {updated}, Failed: {failed}\n")


def main():
    db = SessionLocal()
    try:
        step1_extract_video_ids(db)
        step2_backfill_channel_info(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
