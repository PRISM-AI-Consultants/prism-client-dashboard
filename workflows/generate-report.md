# Workflow: Generate Report

## Purpose
Scrape YouTube analytics data via yt-dlp, analyze trends, generate a PDF report, and email it.

## Inputs
- `channel_url` (string): The YouTube channel URL to analyze (e.g., `https://www.youtube.com/@ChannelName`)
- `max_videos` (integer): Number of recent videos to fetch (default 30)
- `email_to` (string): Recipient email address for the report

## Steps
1. [Tool: scrape-youtube-data] — Fetch channel metadata and recent video data for {channel_url} using yt-dlp
2. [Tool: analyze-trends] — Process raw data to identify performance trends, top videos, and growth metrics
3. [Tool: generate-pdf] — Render analysis results into a formatted PDF report saved to `tmp/`
4. [Tool: send-email] — Email the PDF report to {email_to}

## Outputs
- `report_path` (string): Path to the generated PDF in `tmp/`
- `email_status` (string): Confirmation that the email was sent

## Error Handling
- On step 1 failure (scraping error): retry once with backoff, then fail with `transient` error
- On step 2 failure: fail with `permanent` error — cannot generate report without data
- On step 3 failure: return raw analysis as JSON fallback, flag as `partial`
- On step 4 failure: return report path to user, flag email as unsent
