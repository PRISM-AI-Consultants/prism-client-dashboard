"""
PRISM Client Dashboard
WAT Framework — Tools Layer

Run with: python -m streamlit run tools/prism-dashboard/app.py
"""

import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

TIER_CAPS: dict[str, float | None] = {
    "PRISM Core": 40.0,
    "PRISM Scale": 80.0,
    "PRISM Activation": 10.0,
    "PRISM Momentum Sprint": 60.0,
    "Hourly/Session": None,
}

TIERS = list(TIER_CAPS.keys())
STATUSES = ["On Track", "At Risk", "Behind", "Complete"]
TIER2 = {"PRISM Activation", "PRISM Momentum Sprint"}
ALERT_THRESHOLD = 80.0

DEFAULT_CLIENTS = [
    {"id": 1,  "name": "Jerry Green",      "tier": "PRISM Core",            "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 2,  "name": "Jim Socci",        "tier": "PRISM Core",            "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 3,  "name": "Fronce Barnes",    "tier": "PRISM Scale",           "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 4,  "name": "Jessie Ifill",     "tier": "PRISM Core",            "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 5,  "name": "Will Brown",       "tier": "PRISM Activation",      "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 6,  "name": "Tom Kerchner",     "tier": "PRISM Scale",           "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 7,  "name": "Allan Babbit",     "tier": "PRISM Momentum Sprint", "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 8,  "name": "Trisha Robinson",  "tier": "PRISM Core",            "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 9,  "name": "Virginia Ellen",   "tier": "PRISM Core",            "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
    {"id": 10, "name": "Jean Oursler",     "tier": "Hourly/Session",        "hours_used": 0.0, "deliverable_status": "On Track", "notes": ""},
]

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_data() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_CLIENTS)
        return DEFAULT_CLIENTS
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return raw.get("clients", DEFAULT_CLIENTS)


def save_data(clients: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"clients": clients}, f, indent=2)


def next_id(clients: list[dict]) -> int:
    return max((c["id"] for c in clients), default=0) + 1


def compute_df(clients: list[dict]) -> pd.DataFrame:
    rows = []
    for c in clients:
        tier = c.get("tier", "PRISM Core")
        if tier not in TIER_CAPS:
            tier = "PRISM Core"
        cap = TIER_CAPS[tier]
        used = max(0.0, float(c.get("hours_used", 0.0)))

        if cap is not None:
            remaining: float | str = round(cap - used, 1)
            pct: float | None = round((used / cap) * 100, 1) if cap > 0 else 0.0
        else:
            remaining = "N/A"
            pct = None

        rows.append({
            "_id": c["id"],
            "Client Name": c["name"],
            "Current Tier": tier,
            "Cap (Hrs)": cap if cap is not None else "Unlimited",
            "Hours Used": used,
            "Hours Remaining": remaining,
            "% Used": pct,
            "Status": c.get("deliverable_status", "On Track"),
            "Notes": c.get("notes", ""),
        })
    return pd.DataFrame(rows)


def style_row(row: pd.Series) -> list[str]:
    pct = row["% Used"]
    if pct is None:
        color = ""
    elif pct >= 90:
        color = C["row_red"]
    elif pct >= 75:
        color = C["row_yellow"]
    else:
        color = C["row_green"]
    return [color] * len(row)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PRISM Client Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark mode toggle (persisted in session state)
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

LIGHT = {
    "bg":         "#FFFFFF",
    "sidebar_bg": "#F5F7FF",
    "card_bg":    "#FFFFFF",
    "card_border":"#E0E7FF",
    "text":       "#1A1A2E",
    "heading":    "#2C3E7A",
    "table_border":"#C7D7FF",
    "row_green":  "background-color: #D6F5E3; color: #145A32;",
    "row_yellow": "background-color: #FFF4CC; color: #7A5C00;",
    "row_red":    "background-color: #FFD6D6; color: #8B0000;",
}
DARK = {
    "bg":         "#0E1117",
    "sidebar_bg": "#1A1F2E",
    "card_bg":    "#1E2330",
    "card_border":"#2E3A5C",
    "text":       "#E8EAED",
    "heading":    "#7EB8F7",
    "table_border":"#2E3A5C",
    "row_green":  "background-color: #1A3A2A; color: #6FCF97;",
    "row_yellow": "background-color: #3A3010; color: #F2C94C;",
    "row_red":    "background-color: #3A1010; color: #EB5757;",
}

C = DARK if st.session_state.dark_mode else LIGHT

st.markdown(f"""
<style>
    .stApp {{ background-color: {C['bg']}; color: {C['text']}; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
    h1 {{ color: {C['text']}; font-weight: 800; }}
    h2, h3 {{ color: {C['heading']}; }}
    .stMetric {{
        background: {C['card_bg']};
        border: 1px solid {C['card_border']};
        border-radius: 10px;
        padding: 0.75rem 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }}
    div[data-testid="stDataFrameResizable"] {{
        border: 1px solid {C['table_border']};
        border-radius: 8px;
    }}
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
    }}
    [data-testid="stSidebar"] {{ background-color: {C['sidebar_bg']}; }}
    p, label, .stCaption {{ color: {C['text']} !important; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

LOGO_FILE = os.path.join(os.path.dirname(__file__), "prism_logo.png")

col_logo, col_title, col_date = st.columns([1, 4, 1])
with col_logo:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=120)
with col_title:
    st.title("Client Dashboard")
    st.caption("Daily Huddle — Hour Cap Tracking & Deliverable Status")
with col_date:
    st.markdown(f"**{datetime.now().strftime('%B %d, %Y')}**")
    st.caption(f"Updated {datetime.now().strftime('%I:%M %p')}")

st.divider()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

clients = load_data()
df = compute_df(clients)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=160)
    dark = st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dark_toggle")
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.divider()
    st.header("Filters")
    selected_tiers = st.multiselect("Tier", options=TIERS, default=TIERS)
    selected_statuses = st.multiselect("Status", options=STATUSES, default=STATUSES)

    st.divider()
    st.markdown("**Color Legend**")
    st.success("On Track — < 75% used")
    st.warning("Warning — 75–90% used")
    st.error("Critical — > 90% used")

    st.divider()
    st.markdown("**Tier Reference**")
    for tier, cap in TIER_CAPS.items():
        cap_str = f"{cap} hrs" if cap else "Unlimited"
        tier_num = 3 if tier == "Hourly/Session" else (2 if tier in TIER2 else 1)
        st.markdown(f"- **T{tier_num}** {tier}: `{cap_str}`")

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------

capped = df[df["% Used"].notna()]
critical_count = int((capped["% Used"] >= 90).sum())
warning_count  = int(((capped["% Used"] >= 75) & (capped["% Used"] < 90)).sum())
ok_count       = int((capped["% Used"] < 75).sum())
session_count  = int(df["% Used"].isna().sum())

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Clients", len(df))
m2.metric("On Track", ok_count)
m3.metric("Warning", warning_count)
m4.metric("Critical", critical_count)
m5.metric("Hourly / Session", session_count)

# ---------------------------------------------------------------------------
# Tier 2 cap alerts
# ---------------------------------------------------------------------------

tier2_alerts = df[
    df["Current Tier"].isin(TIER2) &
    df["% Used"].notna() &
    (df["% Used"] >= ALERT_THRESHOLD)
]

if not tier2_alerts.empty:
    st.error(f"CAP ALERT — {len(tier2_alerts)} fixed-engagement client(s) at {ALERT_THRESHOLD:.0f}%+ capacity.")
    for _, row in tier2_alerts.iterrows():
        pct = row["% Used"]
        icon = "🔴" if pct >= 100 else "🟡"
        msg = "CAP EXCEEDED — change order required" if pct >= 100 else "Approaching cap — review scope"
        st.warning(f"{icon} **{row['Client Name']}** ({row['Current Tier']}) — `{row['Hours Used']}/{row['Cap (Hrs)']} hrs ({pct}%)` — {msg}")

st.divider()

# ---------------------------------------------------------------------------
# Editable client table
# ---------------------------------------------------------------------------

st.subheader("Client Hour Tracker")
st.caption("Edit Hours Used, Tier, Status, and Notes inline. Click **Save Changes** to persist.")

mask = df["Current Tier"].isin(selected_tiers) & df["Status"].isin(selected_statuses)
filtered_df = df[mask].copy()

DISPLAY_COLS = ["Client Name", "Current Tier", "Cap (Hrs)", "Hours Used", "Hours Remaining", "% Used", "Status", "Notes"]

edited = st.data_editor(
    filtered_df[DISPLAY_COLS],
    use_container_width=True,
    num_rows="fixed",
    hide_index=True,
    key="client_editor",
    column_config={
        "Client Name": st.column_config.TextColumn("Client Name", disabled=True, width="medium"),
        "Current Tier": st.column_config.SelectboxColumn("Current Tier", options=TIERS, required=True, width="medium"),
        "Cap (Hrs)": st.column_config.TextColumn("Cap (Hrs)", disabled=True, width="small", help="Auto-set by tier."),
        "Hours Used": st.column_config.NumberColumn("Hours Used", min_value=0.0, step=0.5, format="%.1f", width="small"),
        "Hours Remaining": st.column_config.TextColumn("Remaining", disabled=True, width="small"),
        "% Used": st.column_config.ProgressColumn("% Used", min_value=0, max_value=100, format="%.1f%%", width="small"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUSES, required=True, width="small"),
        "Notes": st.column_config.TextColumn("Notes", width="large"),
    },
)

col_save, col_reset, _ = st.columns([1, 1, 6])
with col_save:
    if st.button("Save Changes", type="primary", use_container_width=True):
        name_to_edits = edited.set_index("Client Name").to_dict(orient="index")
        changed = 0
        for client in clients:
            if client["name"] in name_to_edits:
                row = name_to_edits[client["name"]]
                new_tier  = row["Current Tier"] if row["Current Tier"] in TIER_CAPS else client["tier"]
                new_hours = max(0.0, float(row["Hours Used"]))
                if (client["tier"] != new_tier or client["hours_used"] != new_hours
                        or client["deliverable_status"] != row["Status"] or client["notes"] != row["Notes"]):
                    client["tier"]               = new_tier
                    client["hours_used"]         = new_hours
                    client["deliverable_status"] = row["Status"]
                    client["notes"]              = row["Notes"]
                    changed += 1
        save_data(clients)
        if changed:
            st.success(f"Saved — {changed} client(s) updated.")
        else:
            st.info("No changes detected.")
        st.rerun()

with col_reset:
    if st.button("Reset View", use_container_width=True):
        st.rerun()

# ---------------------------------------------------------------------------
# Add New Client
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Add New Client")

with st.form("add_client_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_name = st.text_input("Client Name *", placeholder="e.g. Jane Smith")
    with col2:
        new_tier = st.selectbox("Tier *", options=TIERS)
    with col3:
        new_hours = st.number_input("Hours Used", min_value=0.0, step=0.5, value=0.0, format="%.1f")

    col4, col5 = st.columns(2)
    with col4:
        new_status = st.selectbox("Deliverable Status", options=STATUSES)
    with col5:
        new_notes = st.text_input("Notes", placeholder="Optional notes...")

    submitted = st.form_submit_button("Add Client", type="primary", use_container_width=True)

    if submitted:
        if not new_name.strip():
            st.error("Client Name is required.")
        elif any(c["name"].lower() == new_name.strip().lower() for c in clients):
            st.error(f'"{new_name.strip()}" already exists.')
        else:
            clients.append({
                "id": next_id(clients),
                "name": new_name.strip(),
                "tier": new_tier,
                "hours_used": float(new_hours),
                "deliverable_status": new_status,
                "notes": new_notes.strip(),
            })
            save_data(clients)
            st.success(f'Client "{new_name.strip()}" added successfully!')
            st.rerun()

# ---------------------------------------------------------------------------
# Color-coded overview
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Hour Utilization Overview")
st.caption("Color-coded by % of cap used. Read-only.")

summary_df = filtered_df[["Client Name", "Current Tier", "Cap (Hrs)", "Hours Used", "Hours Remaining", "% Used", "Status"]].copy()
styled = summary_df.style.apply(style_row, axis=1).format(
    {"Hours Used": "{:.1f}", "% Used": lambda v: f"{v:.1f}%" if v is not None else "N/A"},
    na_rep="N/A",
)
st.dataframe(styled, use_container_width=True, hide_index=True)
