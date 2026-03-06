# Workflow: PRISM Dashboard Logic

## Purpose
Define the business rules for calculating client hour utilization, triggering alerts, and rendering the PRISM Client Dashboard.

## Inputs
- `client.tier` (string): The PRISM product tier assigned to the client
- `client.hours_used` (float): Hours logged against the client this period
- `client.deliverable_status` (string): Current delivery state

---

## Step 1: Resolve the Hour Cap

Look up the cap based on the client's current tier:

| Tier | Cap |
|------|-----|
| PRISM Core | 40 hrs/month |
| PRISM Scale | 80 hrs/month |
| PRISM Activation | 10 hrs TOTAL |
| PRISM Momentum Sprint | 60 hrs TOTAL |
| Hourly/Session | None (unlimited) |

**Formula:**
```
cap = TIER_CAPS[client.tier]
```

---

## Step 2: Calculate Derived Fields

```
hours_remaining = cap - hours_used          # If cap is None → display "N/A"
pct_used        = (hours_used / cap) * 100  # If cap is None → display None
```

---

## Step 3: Determine Color Status

Apply the following thresholds to `pct_used`:

| Condition | Color | Label |
|-----------|-------|-------|
| pct_used < 75% | Green (#ccffcc) | On Track |
| 75% <= pct_used < 90% | Yellow (#fff3cc) | Warning |
| pct_used >= 90% | Red (#ffcccc) | Critical |
| cap is None | White (neutral) | N/A |

---

## Step 4: Fire Tier 2 Cap Alerts

Tier 2 products (PRISM Activation, PRISM Momentum Sprint) are **fixed engagements** — once the cap is hit, no more hours can be billed without a change order.

**Alert Rule:**
```
IF client.tier IN ["PRISM Activation", "PRISM Momentum Sprint"]
AND pct_used >= 80
THEN display a CAP ALERT banner at the top of the dashboard
```

- At 80%: Yellow warning banner — "Approaching cap, review scope"
- At 100%+: Red error banner — "Cap exceeded, change order required"

---

## Step 5: Persist Edits

When the user saves changes in the dashboard:
1. Read the current `data.json`
2. Merge edited fields: `hours_used`, `tier`, `deliverable_status`, `notes`
3. Write updated `data.json`
4. Recompute all derived fields
5. Re-render the dashboard

**Fields that are always computed (never stored):**
- `hours_remaining`
- `pct_used`
- Color status

**Fields that are stored:**
- `name`, `tier`, `hours_used`, `deliverable_status`, `notes`

---

## Outputs
- Updated `data.json` with persisted client data
- Rendered Streamlit dashboard with color-coded rows and cap alerts

## Error Handling
- If `data.json` is missing: initialize from `DEFAULT_CLIENTS` constant in `app.py`
- If `hours_used` is negative: clamp to 0 before saving
- If `tier` is unrecognized: default to "PRISM Core"
