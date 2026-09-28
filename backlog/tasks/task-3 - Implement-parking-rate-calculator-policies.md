---
id: TASK-3
title: Implement parking rate calculator policies
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 15:51'
updated_date: '2026-09-28 22:36'
labels:
  - backend
  - billing
  - pricing
dependencies:
  - TASK-2
references:
  - specs/PRD1.md
  - specs/SRS1.md
priority: high
type: feature
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The PRD requires the billing engine to evaluate every applicable pricing policy for a parking stay and charge the lowest valid amount. SRS1 recommends Python policy classes for this behavior because the rules include floating hourly blocks, partial peak overlap, same-day and next-day windows, public holiday handling, loyalty discounts, vehicle multipliers, and the greater-than-24-hour special-rate invalidation rule.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The calculator evaluates Standard Hourly, Early Bird, and Night Owl policies for each completed parking session.
- [x] #2 Standard Hourly rounds duration up to full hours and rates floating hourly blocks from the entry timestamp.
- [x] #3 Standard Hourly applies first-hour, second-hour, and subsequent-hour base car rates from the PRD.
- [x] #4 Weekday peak surcharge is applied to any hourly block that partially overlaps 07:00-10:00 or 16:00-19:00, with public holidays excluded from weekdays.
- [x] #5 Early Bird applies only for same-day entry between 06:00 inclusive and 09:00 exclusive and exit between 15:30 inclusive and 19:00 exclusive.
- [x] #6 Night Owl applies only for entry between 18:00 inclusive and the end of day inclusive and exit between 05:00 inclusive and 10:00 exclusive on the next consecutive day.
- [x] #7 Early Bird and Night Owl apply SILVER, GOLD, and PLATINUM loyalty discounts from the PRD.
- [x] #8 Vehicle multipliers are applied consistently to the selected base policy amount.
- [x] #9 Stays longer than 24 hours invalidate Early Bird and Night Owl and use Standard Hourly only.
- [x] #10 The calculator persists one RateEvaluation per policy considered and selects the cheapest applicable evaluation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add shared Decimal pricing constants and reusable date/time helpers. 2. Implement Standard Hourly policy behavior and audit details. 3. Implement Early Bird and Night Owl special policies with loyalty discounts and >24h invalidation. 4. Add a calculator that persists every policy evaluation and selects the cheapest applicable charge. 5. Verify the full pricing layer inside Podman Compose containers.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via TASK-3.1 through TASK-3.4. The pricing layer now includes shared PRD constants, Standard Hourly, Early Bird, Night Owl, and ParkingRateCalculator persistence/orchestration.

Final verification ran inside Podman Compose containers after rebuilding the image: makemigrations --check --dry-run reported no changes, Django check reported no issues, and the compose test service passed 46 tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the parking rate calculator policies and persistence flow. The calculator evaluates Standard Hourly, Early Bird, and Night Owl, applies vehicle multipliers and loyalty discounts, persists RateEvaluation audit records, and selects the lowest applicable charge. Verified inside Podman Compose with migration dry-run, Django check, and 46 passing tests.
<!-- SECTION:FINAL_SUMMARY:END -->
