"""Analyze Trends Tool

Analyzes video performance data and identifies trends.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime


def main(channel_stats: dict, videos: list) -> dict:
    """Analyze YouTube video data for trends and insights.

    Args:
        channel_stats: Channel-level statistics.
        videos: List of video objects with performance metrics.

    Returns:
        dict with 'top_videos', 'growth_trend', and 'engagement_summary'.
    """
    if not videos:
        return {
            "ok": False,
            "error": {
                "code": "ANALYZE_TRENDS/VALIDATION",
                "message": "No video data provided for analysis.",
                "detail": {},
                "retryable": False,
            },
        }

    # --- Top videos by view count ---
    sorted_by_views = sorted(videos, key=lambda v: v.get("view_count", 0), reverse=True)
    top_videos = []
    for v in sorted_by_views[:5]:
        views = v.get("view_count", 0)
        likes = v.get("like_count", 0)
        comments = v.get("comment_count", 0)
        engagement = (likes + comments) / views if views > 0 else 0
        top_videos.append({
            "title": v.get("title", ""),
            "video_id": v.get("video_id", ""),
            "view_count": views,
            "like_count": likes,
            "comment_count": comments,
            "engagement_ratio": round(engagement, 4),
            "upload_date": v.get("upload_date", ""),
        })

    # --- Aggregate stats ---
    total_views = sum(v.get("view_count", 0) for v in videos)
    total_likes = sum(v.get("like_count", 0) for v in videos)
    total_comments = sum(v.get("comment_count", 0) for v in videos)
    avg_views = total_views / len(videos) if videos else 0
    avg_likes = total_likes / len(videos) if videos else 0
    avg_comments = total_comments / len(videos) if videos else 0
    overall_engagement = (total_likes + total_comments) / total_views if total_views > 0 else 0

    engagement_summary = {
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "avg_views_per_video": round(avg_views),
        "avg_likes_per_video": round(avg_likes),
        "avg_comments_per_video": round(avg_comments),
        "overall_engagement_ratio": round(overall_engagement, 4),
        "video_count": len(videos),
    }

    # --- Publishing frequency by month ---
    monthly_counts = defaultdict(int)
    monthly_views = defaultdict(int)
    for v in videos:
        date_str = v.get("upload_date", "")
        if len(date_str) >= 6:
            month_key = f"{date_str[:4]}-{date_str[4:6]}"
            monthly_counts[month_key] += 1
            monthly_views[month_key] += v.get("view_count", 0)

    months_sorted = sorted(monthly_counts.keys())
    publishing_trend = []
    for m in months_sorted:
        publishing_trend.append({
            "month": m,
            "videos_published": monthly_counts[m],
            "total_views": monthly_views[m],
            "avg_views": round(monthly_views[m] / monthly_counts[m]) if monthly_counts[m] > 0 else 0,
        })

    # --- Growth trend (compare first half vs second half) ---
    dated_videos = [v for v in videos if v.get("upload_date")]
    dated_videos.sort(key=lambda v: v["upload_date"])
    mid = len(dated_videos) // 2
    if mid > 0:
        first_half_avg = sum(v.get("view_count", 0) for v in dated_videos[:mid]) / mid
        second_half_avg = sum(v.get("view_count", 0) for v in dated_videos[mid:]) / (len(dated_videos) - mid)
        growth_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
        growth_trend = {
            "older_half_avg_views": round(first_half_avg),
            "newer_half_avg_views": round(second_half_avg),
            "growth_percent": round(growth_pct, 1),
            "direction": "up" if growth_pct > 0 else "down" if growth_pct < 0 else "flat",
        }
    else:
        growth_trend = {
            "older_half_avg_views": 0,
            "newer_half_avg_views": 0,
            "growth_percent": 0,
            "direction": "insufficient_data",
        }

    # --- Best and worst performers ---
    best = sorted_by_views[0] if sorted_by_views else None
    worst = sorted_by_views[-1] if sorted_by_views else None

    return {
        "ok": True,
        "result": {
            "top_videos": top_videos,
            "growth_trend": growth_trend,
            "engagement_summary": engagement_summary,
            "publishing_trend": publishing_trend,
            "best_performer": {
                "title": best.get("title", ""),
                "view_count": best.get("view_count", 0),
            } if best else None,
            "worst_performer": {
                "title": worst.get("title", ""),
                "view_count": worst.get("view_count", 0),
            } if worst else None,
        },
    }


if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    result = main(
        channel_stats=data.get("channel_stats", {}),
        videos=data.get("videos", []),
    )
    print(json.dumps(result, indent=2))
