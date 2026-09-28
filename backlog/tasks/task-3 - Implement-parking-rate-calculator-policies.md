---
id: TASK-3
title: Implement parking rate calculator policies
status: To Do
assignee: []
created_date: '2026-09-28 15:51'
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
- [ ] #1 The calculator evaluates Standard Hourly, Early Bird, and Night Owl policies for each completed parking session.
- [ ] #2 Standard Hourly rounds duration up to full hours and rates floating hourly blocks from the entry timestamp.
- [ ] #3 Standard Hourly applies first-hour, second-hour, and subsequent-hour base car rates from the PRD.
- [ ] #4 Weekday peak surcharge is applied to any hourly block that partially overlaps 07:00-10:00 or 16:00-19:00, with public holidays excluded from weekdays.
- [ ] #5 Early Bird applies only for same-day entry between 06:00 inclusive and 09:00 exclusive and exit between 15:30 inclusive and 19:00 exclusive.
- [ ] #6 Night Owl applies only for entry between 18:00 inclusive and the end of day inclusive and exit between 05:00 inclusive and 10:00 exclusive on the next consecutive day.
- [ ] #7 Early Bird and Night Owl apply SILVER, GOLD, and PLATINUM loyalty discounts from the PRD.
- [ ] #8 Vehicle multipliers are applied consistently to the selected base policy amount.
- [ ] #9 Stays longer than 24 hours invalidate Early Bird and Night Owl and use Standard Hourly only.
- [ ] #10 The calculator persists one RateEvaluation per policy considered and selects the cheapest applicable evaluation.
<!-- AC:END -->
