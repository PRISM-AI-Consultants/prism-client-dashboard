"""Scrape YouTube Data Tool

Fetches channel and video metadata using yt-dlp (no API key required).
"""

import json
import sys

import yt_dlp


def main(channel_url: str, max_videos: int = 30) -> dict:
    """Fetch channel stats and recent video data using yt-dlp.

    Args:
        channel_url: YouTube channel URL (e.g. https://www.youtube.com/@ChannelName).
        max_videos: Maximum number of recent videos to retrieve.

    Returns:
        dict with 'channel_stats' and 'videos' keys.
    """
    if not channel_url:
        return {
            "ok": False,
            "error": {
                "code": "SCRAPE_YOUTUBE_DATA/VALIDATION",
                "message": "channel_url is required.",
                "detail": {},
                "retryable": False,
            },
        }

    # Normalize URL to the channel's videos tab
    url = channel_url.rstrip("/")
    if not url.endswith("/videos"):
        url += "/videos"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": max_videos,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        return {
            "ok": False,
            "error": {
                "code": "SCRAPE_YOUTUBE_DATA/TRANSIENT",
                "message": f"Failed to fetch channel data: {e}",
                "detail": {},
                "retryable": True,
            },
        }

    if not playlist_info:
        return {
            "ok": False,
            "error": {
                "code": "SCRAPE_YOUTUBE_DATA/PERMANENT",
                "message": "No data returned for the given channel URL.",
                "detail": {},
                "retryable": False,
            },
        }

    # Extract channel-level stats from the playlist metadata
    channel_stats = {
        "channel_name": playlist_info.get("channel") or playlist_info.get("uploader", "Unknown"),
        "channel_id": playlist_info.get("channel_id", ""),
        "channel_url": playlist_info.get("channel_url") or channel_url,
        "description": playlist_info.get("description", ""),
    }

    # Now fetch detailed metadata for each video
    entries = playlist_info.get("entries") or []
    video_ids = [e["id"] for e in entries if e and e.get("id")]

    videos = []
    if video_ids:
        detail_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(detail_opts) as ydl:
            for vid_id in video_ids:
                try:
                    info = ydl.extract_info(
                        f"https://www.youtube.com/watch?v={vid_id}",
                        download=False,
                    )
                    if info:
                        videos.append({
                            "video_id": info.get("id", vid_id),
                            "title": info.get("title", ""),
                            "upload_date": info.get("upload_date", ""),
                            "view_count": info.get("view_count", 0) or 0,
                            "like_count": info.get("like_count", 0) or 0,
                            "comment_count": info.get("comment_count", 0) or 0,
                            "duration": info.get("duration", 0) or 0,
                            "url": info.get("webpage_url", f"https://www.youtube.com/watch?v={vid_id}"),
                        })
                except Exception:
                    # Skip videos that fail to extract
                    continue

    channel_stats["total_videos_fetched"] = len(videos)

    return {
        "ok": True,
        "result": {
            "channel_stats": channel_stats,
            "videos": videos,
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "ok": False,
            "error": {
                "code": "SCRAPE_YOUTUBE_DATA/VALIDATION",
                "message": "Usage: python index.py <channel_url> [max_videos]",
            },
        }))
        sys.exit(1)

    result = main(
        channel_url=sys.argv[1],
        max_videos=int(sys.argv[2]) if len(sys.argv) > 2 else 30,
    )
    print(json.dumps(result, indent=2))
