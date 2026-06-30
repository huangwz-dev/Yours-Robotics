# Walkthrough

> A written walkthrough (the brief accepts this *or* a 3–5 min screen recording). Read this
> aloud while clicking through the dashboard if you record a video. Edit it into your own
> words first.

## 1. What this is (30s)

A Fleet Ops Console for the PDD robot pilot. It ingests six raw CSV exports, cleans them,
computes operational metrics, and presents them on a single dashboard a non-engineer can read.
Stack: **Python + Flask** API, **dependency-free HTML/JS** frontend (no Node toolchain needed).

## 2. How to run it (30s)

```powershell
# Backend
cd backend
py -m pip install -r requirements.txt
py app.py                 # serves the API on http://localhost:5000

# Frontend (new terminal, from the repo root)
py -m http.server 3000    # then open http://localhost:3000
```

## 3. The dashboard (90s)

- **Fleet overview:** total vs active robots, QR conversion rate (~33%), and total vending
  revenue. Below that, every robot with its last-known state and availability; robots under
  50% availability are flagged.
- **Per-robot drill-down:** click any robot to see its zone, deploy date, availability,
  interactions, vending revenue, navigation events, and fault count.
- **Data-quality panel:** the metric definitions plus every anomaly the pipeline detected —
  this is how an operator knows what to trust before reading the numbers.

## 4. Data quality — the interesting part (60s)

The pipeline auto-detects and reports four issues, all listed in `summary.json`:
- `footfall.csv` zone names with underscores (`PDD_A`) — normalised to `PDD-A`.
- 25 `nav_events.csv` rows with blank severity — treated as non-faults.
- **`R-99`** appears in telemetry but isn't a registered robot — excluded from fleet totals
  (this is what was making "active robots" exceed "total robots").
- Mixed-case `state` values in telemetry — lower-cased before aggregating.

## 5. Judgment calls & what I'd do next (30s)

- Availability is a day-level "did we hear from it" measure — conservative and operator-
  friendly; I'd move to expected-vs-actual sample counts with more time.
- Some QR sessions are flagged `converted=true` despite an `abandoned` outcome — I'd confirm
  that with the data owner before fully trusting the funnel.
- Next: automated alerting, time-series charts, and unit tests around the cleaning rules.

See `DECISIONS.md` for the full reasoning.
