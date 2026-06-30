# DECISIONS

This document records the assumptions, metric definitions, and trade-offs behind the Fleet
Ops Console. Where the brief left a term undefined, I picked a sensible definition, stated it,
and explained why.

## Metric definitions

- **Availability / uptime:** The percentage of the 14 pilot days (1–14 Jun 2026) on which a
  robot produced **at least one telemetry reading**. I chose a *day-level presence* measure
  rather than a time-weighted one because telemetry is sampled at coarse, irregular intervals
  (roughly half-hourly), so I cannot reliably reconstruct continuous up/down intervals. A
  robot that reported on all 14 days scores 100%. This is intentionally conservative and easy
  for an operator to reason about ("did we hear from it today?").
  - *Trade-off:* it does not distinguish a robot that was up all day from one that pinged
    once. With more time I would switch to expected-vs-actual telemetry sample counts per day.

- **Active robot:** A robot **registered in `robots.csv`** that produced at least one
  telemetry reading during the pilot window. The "registered" constraint matters: telemetry
  contains a robot (`R-99`) that is not in the fleet registry, which would otherwise push the
  active count above the total fleet size.

- **QR conversion rate:** `conversions / total QR scans`, where a scan counts as converted
  when its `converted` flag is true. Computed only over rows where `type == 'qr_scan'`.

- **Fault:** A navigation event with `severity == 'warn'`. Blank-severity events are treated
  as non-faults (see data quality below).

## Assumptions I made

- The pilot window is 1–14 Jun 2026 (14 days), inferred from the telemetry/interaction
  timestamp range. Footfall starts slightly earlier (31 May), which I treat as sensor
  warm-up and ignore for per-robot day counts.
- Vending **revenue** counts only `payment_status == 'paid'` rows. `failed` and `refunded`
  transactions are excluded from revenue and from the counted-transaction total.
- A QR `converted` flag of `true` is trusted even when the row's `outcome` is `abandoned` or
  `error`; the conversion flag and the session outcome are independent signals. (Worth
  revisiting — see known issues.)
- Each robot's zone for zone-level aggregation is its `home_zone` from the registry, not the
  zone in each telemetry row.

## Data quality — what I found and how I handled it

- **Zone name inconsistency (`footfall.csv`):** 50 rows use `PDD_A` (underscore) instead of
  `PDD-A`. Normalised underscores to dashes before aggregating footfall by zone.
- **Missing severity (`nav_events.csv`):** 25 events have a blank `severity`. Left as-is and
  treated as non-faults so they do not inflate the fault count.
- **Unregistered robot (`R-99`):** Present in telemetry but absent from `robots.csv`.
  Excluded from fleet metrics and surfaced as an anomaly.
- **State case inconsistency (`telemetry.csv`):** `state` mixes cases (e.g. `charging` vs
  `CHARGING`). Lower-cased all states before computing per-state metrics.

## What I prioritised, and what I deliberately left out

- **Built first:** the data-ingestion + cleaning layer and the core metrics (availability,
  engagement, QR funnel, vending, faults), because correctness of the numbers is the
  foundation everything else rests on.
- **Then:** a single-page dashboard (fleet overview, per-robot drill-down, data-quality
  panel) so a non-engineer can read the fleet at a glance.
- **Cut for time:** automated anomaly *alerting*, time-series charts, authentication, and a
  build-tooled React app. The frontend is a dependency-free static page that talks to the
  Flask API, which keeps the project runnable from a clean clone without a Node toolchain.

## Known issues / what I'd do with another day

- Availability is day-level, not time-weighted; I would move to expected-vs-actual sample
  counts for a truer uptime figure.
- The `converted=true` on `abandoned`/`error` sessions is suspicious and may be a logging
  bug; I would confirm with whoever owns the interactions pipeline before fully trusting the
  QR conversion rate.
- No automated tests yet. I would add unit tests around the cleaning rules and the metric
  calculations, with small fixture CSVs.
- The dashboard reloads the page to exit a drill-down; a small client-side state fix would
  make it smoother.
