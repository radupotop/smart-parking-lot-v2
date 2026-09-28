# Entity Relationship Diagram

Customers: id (int) | loyalty_tier (str) | created_at (datetime) | updated_at (datetime)
# `loyalty_tier` is one of NONE, SILVER, GOLD, or PLATINUM. The
# tier should also be snapshotted on each parking session so historical
# billing does not change if the customer tier changes later.

Vehicles: id (int) | registration (str) | vehicle_type (str) | customer_id (nullable FK -> Customers) | created_at (datetime) | updated_at (datetime)
# `vehicle_type` is one of MOTORCYCLE, CAR, or BUS. Vehicle rate
# multipliers are fixed domain values in the application code:
# MOTORCYCLE = 0.8x, CAR = 1.0x, BUS = 2.0x.

ParkingSpots: id (int) | level (int) | number (str) | spot_type (str) | created_at (datetime) | updated_at (datetime)
# `spot_type` is one of COMPACT or LARGE. The pair of `level` and
# `number` should be unique.

SpotTypeVehicleCompatibilities: id (int) | spot_type (str) | vehicle_type (str)
# Defines which vehicle types can use which spot types. For example,
# COMPACT can support MOTORCYCLE and CAR, while LARGE supports BUS.
# The pair of `spot_type` and `vehicle_type` should be unique.

ParkingSessions: id (int) | vehicle_id (FK -> Vehicles) | spot_id (FK -> ParkingSpots) | customer_id (nullable FK -> Customers) | entered_at (datetime) | exited_at (nullable datetime) | status (str) | loyalty_tier_snapshot (str) | charged_amount (nullable decimal) | selected_evaluation_id (nullable FK -> RateEvaluations) | created_at (datetime) | updated_at (datetime)
# This is also the ticket record described by the PRD. It stores the
# entry timestamp, optional exit timestamp, assigned vehicle and spot,
# and the final selected charge after policy evaluation.
# `customer_id` and `loyalty_tier_snapshot` capture the billing context
# at the time of the stay.

RateEvaluations: id (int) | session_id (FK -> ParkingSessions) | policy (str) | applicable (bool) | amount (nullable decimal) | details (json) | created_at (datetime)
# Stores the result of evaluating one pricing policy against one
# parking session. `policy` is one of STANDARD, EARLY_BIRD, or NIGHT_OWL.
# `details` stores the audit trail, such as hourly blocks, peak-hour
# flags, vehicle multiplier, loyalty discount, and final amount.

PublicHolidays: id (int) | date (date) | name (str)
# Used by the Standard Hourly policy because weekdays are Monday through
# Friday excluding public holidays. `date` should be unique.

## Relationship Summary

Customers have zero or more Vehicles.

Vehicles belong to zero or one Customer and can have many ParkingSessions.

ParkingSpots can have many ParkingSessions over time.

SpotTypeVehicleCompatibilities define the allowed many-to-many
relationship between spot types and vehicle types.

ParkingSessions belong to one Vehicle and one ParkingSpot. They may also
belong to one Customer when a customer is known for that stay.

ParkingSessions have many RateEvaluations, one per pricing policy
considered by the rate calculator.

ParkingSessions select zero or one RateEvaluation as the final winning
evaluation once billing has been calculated.

PublicHolidays are referenced by pricing logic, not by a direct foreign
key, when deciding whether a date counts as a weekday for peak pricing.
