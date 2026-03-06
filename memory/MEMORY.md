# Project Memory

## Project
YouTube Analytics Automation — WAT Framework

## Goal
Scrape YouTube data, analyze trends, generate a PDF report, and email it.

## Key Decisions
- Tools are implemented in Python
- YouTube data scraped via **yt-dlp** (no API key required)
- PDF reports generated with **fpdf2**
- Email sent via **smtplib** with STARTTLS
- SMTP credentials stored in `.env`
- Temporary/intermediate files go in `tmp/`
- Dependencies: `yt-dlp`, `fpdf2`, `python-dotenv`

## Status
All four tools implemented: scrape-youtube-data, analyze-trends, generate-pdf, send-email.
