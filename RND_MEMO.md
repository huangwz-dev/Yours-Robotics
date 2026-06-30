# R&D Memo — Proposed Capability: Zone-Aware Promo Conversion Engine

> ⚠️ This is a draft to react to and rewrite in your own voice. The reviewers assess the memo
> on commercial viability and *your* judgment — make the idea yours before submitting.

## The capability

Give each robot a **zone-aware promo engine**: the robot chooses *which* campaign/offer to
show on its screen based on real-time context it already has — current zone, time of day,
live footfall density, and recent QR conversion performance for each campaign in that zone.
Today the fleet shows campaigns; it does not yet *optimise* which one to show where and when.

## Who would pay, and why

- **Brands running campaigns (primary buyer):** they already pay for screen time. A system
  that lifts conversion rate (currently ~33% on QR scans) directly increases their ROI, so
  they will pay a premium for "smart placement" or a performance-based rate.
- **The venue owner (PDD):** higher engagement and vending revenue per robot strengthens the
  case for expanding the fleet and justifies higher rent/revenue-share.
- **Us (the operator):** better conversion → higher vending revenue and a defensible,
  data-driven upsell over "dumb" digital signage.

## How I'd build it

1. **Offline:** from the existing logs, build a simple per-(zone, hour, campaign) conversion
   model — start with a ranked table, not ML, so it is explainable.
2. **On-robot:** a lightweight policy that picks the highest expected-conversion campaign for
   the robot's current zone/time, with an epsilon-greedy exploration slice so we keep learning.
3. **Feedback loop:** stream scan→conversion outcomes back to refine the table nightly.

## How I'd validate it in the PDD pilot

- **A/B test:** half the fleet runs the engine, half stays on the current fixed rotation, for
  two weeks. Randomise by robot and rotate zones to control for location effects.
- **Primary metric:** QR conversion rate and vending revenue per robot-day.
- **Guardrail metrics:** interaction abandonment rate and fault counts (make sure we are not
  just showing more aggressive prompts).
- **Success bar:** a statistically meaningful lift in conversion in the treatment group with
  no degradation in the guardrails.
