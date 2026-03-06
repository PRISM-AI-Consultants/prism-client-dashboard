"""Generate PDF Tool

Generates a PDF report from analysis results using fpdf2.
"""

import json
import os
import sys
from datetime import datetime

from fpdf import FPDF


class ReportPDF(FPDF):
    """Custom PDF class with header/footer for YouTube analytics reports."""

    def __init__(self, channel_name: str = "YouTube Channel"):
        super().__init__()
        self.channel_name = channel_name

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"{self.channel_name} - Analytics Report", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _fmt_number(n: int) -> str:
    """Format a number with comma separators."""
    return f"{n:,}"


def _fmt_date(date_str: str) -> str:
    """Convert YYYYMMDD to a readable date."""
    if len(date_str) == 8:
        try:
            return datetime.strptime(date_str, "%Y%m%d").strftime("%b %d, %Y")
        except ValueError:
            pass
    return date_str


def main(analysis: dict, channel_stats: dict = None, output_path: str = None) -> dict:
    """Generate a PDF report from YouTube analytics data.

    Args:
        analysis: Analysis results from analyze-trends.
        channel_stats: Optional channel-level stats for the header.
        output_path: Optional path for the PDF (defaults to tmp/).

    Returns:
        dict with 'report_path' pointing to the generated PDF.
    """
    if not analysis:
        return {
            "ok": False,
            "error": {
                "code": "GENERATE_PDF/VALIDATION",
                "message": "No analysis data provided.",
                "detail": {},
                "retryable": False,
            },
        }

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("tmp", f"youtube_report_{timestamp}.pdf")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    channel_name = (channel_stats or {}).get("channel_name", "YouTube Channel")
    pdf = ReportPDF(channel_name=channel_name)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Title Page ──
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 15, "YouTube Analytics Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, channel_name, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 12)
    pdf.cell(0, 10, f"Generated {datetime.now().strftime('%B %d, %Y')}", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Channel Overview ──
    if channel_stats:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Channel Overview", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        overview_items = [
            ("Channel", channel_stats.get("channel_name", "N/A")),
            ("Channel ID", channel_stats.get("channel_id", "N/A")),
            ("Videos Analyzed", str(channel_stats.get("total_videos_fetched", "N/A"))),
        ]
        for label, value in overview_items:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(55, 8, f"{label}:")
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")

    # ── Engagement Summary ──
    engagement = analysis.get("engagement_summary", {})
    if engagement:
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Engagement Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        metrics = [
            ("Total Views", _fmt_number(engagement.get("total_views", 0))),
            ("Total Likes", _fmt_number(engagement.get("total_likes", 0))),
            ("Total Comments", _fmt_number(engagement.get("total_comments", 0))),
            ("Avg Views / Video", _fmt_number(engagement.get("avg_views_per_video", 0))),
            ("Avg Likes / Video", _fmt_number(engagement.get("avg_likes_per_video", 0))),
            ("Engagement Ratio", f"{engagement.get('overall_engagement_ratio', 0):.2%}"),
            ("Videos Analyzed", str(engagement.get("video_count", 0))),
        ]
        for label, value in metrics:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(55, 8, f"{label}:")
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")

    # ── Growth Trend ──
    growth = analysis.get("growth_trend", {})
    if growth and growth.get("direction") != "insufficient_data":
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Growth Trend", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        direction = growth.get("direction", "flat")
        pct = growth.get("growth_percent", 0)
        arrow = "UP" if direction == "up" else "DOWN" if direction == "down" else "--"

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 8, f"Older videos avg views: {_fmt_number(growth.get('older_half_avg_views', 0))}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Newer videos avg views: {_fmt_number(growth.get('newer_half_avg_views', 0))}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 13)
        color = (0, 140, 60) if direction == "up" else (200, 50, 50) if direction == "down" else (100, 100, 100)
        pdf.set_text_color(*color)
        pdf.cell(0, 10, f"{arrow} {pct:+.1f}% change", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(50, 50, 50)

    # ── Top Videos ──
    top_videos = analysis.get("top_videos", [])
    if top_videos:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Top Videos by Views", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Table header
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(8, 8, "#", border=1, fill=True, align="C")
        pdf.cell(80, 8, "Title", border=1, fill=True)
        pdf.cell(25, 8, "Views", border=1, fill=True, align="R")
        pdf.cell(25, 8, "Likes", border=1, fill=True, align="R")
        pdf.cell(25, 8, "Comments", border=1, fill=True, align="R")
        pdf.cell(27, 8, "Date", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

        # Table rows
        pdf.set_font("Helvetica", "", 9)
        for i, v in enumerate(top_videos, 1):
            title = v.get("title", "")
            if len(title) > 45:
                title = title[:42] + "..."
            pdf.cell(8, 8, str(i), border=1, align="C")
            pdf.cell(80, 8, title, border=1)
            pdf.cell(25, 8, _fmt_number(v.get("view_count", 0)), border=1, align="R")
            pdf.cell(25, 8, _fmt_number(v.get("like_count", 0)), border=1, align="R")
            pdf.cell(25, 8, _fmt_number(v.get("comment_count", 0)), border=1, align="R")
            pdf.cell(27, 8, _fmt_date(v.get("upload_date", "")), border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Publishing Trend ──
    pub_trend = analysis.get("publishing_trend", [])
    if pub_trend:
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Publishing Trend by Month", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(30, 8, "Month", border=1, fill=True, align="C")
        pdf.cell(35, 8, "Videos Published", border=1, fill=True, align="R")
        pdf.cell(35, 8, "Total Views", border=1, fill=True, align="R")
        pdf.cell(35, 8, "Avg Views", border=1, fill=True, align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        for entry in pub_trend:
            pdf.cell(30, 8, entry.get("month", ""), border=1, align="C")
            pdf.cell(35, 8, str(entry.get("videos_published", 0)), border=1, align="R")
            pdf.cell(35, 8, _fmt_number(entry.get("total_views", 0)), border=1, align="R")
            pdf.cell(35, 8, _fmt_number(entry.get("avg_views", 0)), border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    # ── Write PDF ──
    try:
        pdf.output(output_path)
    except Exception as e:
        return {
            "ok": False,
            "error": {
                "code": "GENERATE_PDF/PERMANENT",
                "message": f"Failed to write PDF: {e}",
                "detail": {},
                "retryable": False,
            },
        }

    return {
        "ok": True,
        "result": {
            "report_path": os.path.abspath(output_path),
        },
    }


if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    result = main(
        analysis=data.get("analysis", {}),
        channel_stats=data.get("channel_stats"),
        output_path=data.get("output_path"),
    )
    print(json.dumps(result, indent=2))
