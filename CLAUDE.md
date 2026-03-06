# Agent Instructions

You are working inside the **WAT Framework** (Workflows, Agents, Tools).

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, inputs, tools to use, and expected outputs.

**Layer 2: Agents (The Decision-Maker)**
- You are the agent. Read the workflow, run tools in sequence, and handle failures.

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work (scraping, data processing).
- SMTP credentials are stored in `.env`. No API key is needed for YouTube scraping.

## File Structure
- `tmp/`: Temporary files (scraped data, PDFs).
- `tools/`: Python scripts (`.py`).
- `workflows/`: Markdown instructions (`.md`).
- `.env`: SMTP credentials (NEVER store secrets anywhere else).
- `requirements.txt`: Python dependencies.

---

## Project 1: YouTube Analytics Automation

### Goal
Scrape YouTube public video data via yt-dlp, analyze trends, generate a PDF report, and email it.

### Tools
- `tools/scrape-youtube-data/` — fetches video metadata via yt-dlp
- `tools/analyze-trends/` — computes view/engagement trends
- `tools/generate-pdf/` — renders the PDF report with fpdf2
- `tools/send-email/` — sends the report via SMTP

### Dependencies
`yt-dlp`, `fpdf2`, `python-dotenv`

---

## Project 2: PRISM Client Dashboard

### Goal
Interactive Streamlit dashboard for tracking client hours, deliverables, and retainer caps during Daily Huddles.

### Tiers & Business Logic

| Tier | Product | Cap | Type | Alert Threshold |
|------|---------|-----|------|----------------|
| 1 | PRISM Core | 40 hrs/month | Retainer | High Priority |
| 1 | PRISM Scale | 80 hrs/month | Retainer | High Priority |
| 2 | PRISM Activation | 10 hrs TOTAL | Fixed | Alert at 80% |
| 2 | PRISM Momentum Sprint | 60 hrs TOTAL | Fixed | Alert at 80% |
| 3 | Hourly/Session | Unlimited | Per-session | N/A |

### Color Coding
- Green: < 75% of cap used
- Yellow: 75–90% of cap used
- Red: > 90% of cap used

### Tools
- `tools/prism-dashboard/app.py` — Streamlit web app (run with `streamlit run tools/prism-dashboard/app.py`)
- `tools/prism-dashboard/data.json` — persistent client data store

### Workflow
- See `workflows/dashboard_logic.md`

### Run Instructions
```bash
streamlit run tools/prism-dashboard/app.py
```

### Dependencies
`streamlit`, `pandas`
