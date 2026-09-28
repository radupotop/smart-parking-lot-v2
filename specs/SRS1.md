title: Software Requirements Specification 
id: SRS-1

# Software Requirements Specification

I’d keep the **parking domain** relational, but I would *not* try to encode the entire pricing algorithm as rows in the database. The pricing rules have enough behavioural logic—floating hourly blocks, partial peak overlap, same-day/next-day conditions, >24h invalidation—that they belong in Python policy classes. The database should store the inputs, configurable parameters, and an audit trail of what was evaluated.

The important distinction is between a **ticket/session**, which records what actually happened, and **rate policies**, which are alternative ways of pricing that same session. The engine evaluates every applicable policy and selects the cheapest one, as required.

### Core model

I would roughly model it like this:

```text
Customer
 ├── loyalty_tier
 └── vehicles

Vehicle
 ├── registration
 └── vehicle_type

VehicleType
 ├── CAR
 ├── MOTORCYCLE
 └── BUS
      │
      └── rate_multiplier

SpotType
 ├── COMPACT
 └── LARGE

ParkingSpot
 ├── level
 ├── number
 └── spot_type

ParkingSession / Ticket
 ├── vehicle
 ├── spot
 ├── entered_at
 ├── exited_at
 ├── customer
 ├── status
 └── final_charge
       │
       └── selected RateEvaluation

RatePolicy
 ├── STANDARD
 ├── EARLY_BIRD
 └── NIGHT_OWL
       │
       └── RateEvaluation
            ├── session
            ├── applicable
            ├── amount
            └── calculation details
```

The first thing I would avoid is making `Ticket` and `ParkingSession` separate concepts unless the assignment explicitly demands it. In this problem, the ticket is effectively the persisted representation of the stay: entry timestamp, exit timestamp, vehicle, etc. The requirements describe the ticket as the foundational record carrying the entry timestamp.

Something like:

```python
class VehicleType(models.TextChoices):
    MOTORCYCLE = "motorcycle", "Motorcycle"
    CAR = "car", "Car"
    BUS = "bus", "Bus"


class LoyaltyTier(models.TextChoices):
    NONE = "none", "None"
    SILVER = "silver", "Silver"
    GOLD = "gold", "Gold"
    PLATINUM = "platinum", "Platinum"


class Customer(models.Model):
    loyalty_tier = models.CharField(
        max_length=16,
        choices=LoyaltyTier,
        default=LoyaltyTier.NONE,
    )


class Vehicle(models.Model):
    registration = models.CharField(max_length=32, unique=True)

    vehicle_type = models.CharField(
        max_length=16,
        choices=VehicleType,
    )

    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vehicles",
    )
```

For only three fixed vehicle types, I'd probably **not** create a `VehicleType` table. They are domain concepts, not arbitrary user-created data.

The multiplier can then either live in code:

```python
VEHICLE_MULTIPLIERS = {
    VehicleType.MOTORCYCLE: Decimal("0.8"),
    VehicleType.CAR: Decimal("1.0"),
    VehicleType.BUS: Decimal("2.0"),
}
```

or, if management needs to modify it operationally, in a small configuration table.

Those multipliers are global pricing inputs rather than properties of individual vehicles: motorcycle `0.8x`, car `1.0x`, bus `2.0x`.

For spots I'd use:

```python
class SpotType(models.TextChoices):
    COMPACT = "compact", "Compact"
    LARGE = "large", "Large"


class ParkingSpot(models.Model):
    level = models.PositiveSmallIntegerField()
    number = models.CharField(max_length=16)

    spot_type = models.CharField(
        max_length=16,
        choices=SpotType,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["level", "number"],
                name="unique_parking_spot",
            )
        ]
```

There's an interesting modelling issue here: **spot compatibility is many-to-many**. A compact spot can accommodate motorcycles and cars, while a large spot presumably supports buses and possibly other vehicles.

If compatibility might evolve, I would actually represent it:

```python
class SpotTypeVehicleType(models.Model):
    spot_type = models.CharField(
        max_length=16,
        choices=SpotType,
    )
    vehicle_type = models.CharField(
        max_length=16,
        choices=VehicleType,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["spot_type", "vehicle_type"],
                name="unique_spot_vehicle_compatibility",
            )
        ]
```

Although for such a small fixed domain, a code-level mapping would also be reasonable.

### The central table: `ParkingSession`

I'd make this the important transactional record:

```python
class ParkingSession(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
    )

    spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.PROTECT,
    )

    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    entered_at = models.DateTimeField()
    exited_at = models.DateTimeField(null=True, blank=True)

    charged_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    selected_evaluation = models.ForeignKey(
        "RateEvaluation",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
```

I'd deliberately snapshot the relevant customer relationship here instead of assuming that `session.vehicle.customer` forever represents who parked the car at that time.

Depending on the requirements, I'd potentially snapshot the loyalty tier too:

```python
loyalty_tier = models.CharField(
    max_length=16,
    choices=LoyaltyTier,
    default=LoyaltyTier.NONE,
)
```

That matters because if Alice was `SILVER` on Monday and becomes `GOLD` on Friday, recalculating Monday's invoice shouldn't silently change its historical result.

The specials explicitly derive their discount from the customer's loyalty tier.

### I would make policy evaluation a first-class audit record

This is probably the bit I'd care about most.

Don't merely calculate:

```python
session.charged_amount = 12
```

and throw away how you got there.

Instead:

```python
class RatePolicy(models.TextChoices):
    STANDARD = "standard", "Standard hourly"
    EARLY_BIRD = "early_bird", "Early Bird"
    NIGHT_OWL = "night_owl", "Night Owl"


class RateEvaluation(models.Model):
    session = models.ForeignKey(
        ParkingSession,
        on_delete=models.CASCADE,
        related_name="rate_evaluations",
    )

    policy = models.CharField(
        max_length=32,
        choices=RatePolicy,
    )

    applicable = models.BooleanField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    details = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
```

For one stay you might therefore get:

```text
session 123

standard
    applicable = True
    amount = 43.50

early_bird
    applicable = True
    amount = 12.00

night_owl
    applicable = False
    amount = NULL

selected_evaluation = early_bird
charged_amount = 12.00
```

That maps extremely cleanly onto the requirement that **every valid policy must be evaluated and the minimum returned**, rather than just picking the first applicable policy.

And `details` gives you an audit trail:

```json
{
  "base_amount": "15.00",
  "vehicle_multiplier": "1.0",
  "loyalty_tier": "GOLD",
  "loyalty_discount": "0.20",
  "final_amount": "12.00"
}
```

For standard hourly:

```json
{
  "hours": [
    {
      "number": 1,
      "start": "2026-09-28T06:30:00",
      "end": "2026-09-28T07:30:00",
      "base_rate": "5.00",
      "peak": true,
      "peak_multiplier": "1.5",
      "amount": "7.50"
    },
    ...
  ]
}
```

That would make debugging billing disputes vastly easier.

### Rate configuration

There are two reasonable approaches.

For an exercise, I'd probably keep these constants in code:

```python
STANDARD_RATES = (
    Decimal("5.00"),
    Decimal("3.00"),
    Decimal("2.00"),
)

PEAK_MULTIPLIER = Decimal("1.5")
EARLY_BIRD_RATE = Decimal("15.00")
NIGHT_OWL_RATE = Decimal("8.00")
```

The standard pricing has a first-hour `$5`, second-hour `$3`, then `$2` per subsequent hour, with each floating hourly block independently checked for peak overlap.

In a real parking product, though, these will eventually change. I'd therefore probably introduce something like:

```python
class PricingPlan(models.Model):
    name = models.CharField(max_length=100)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)

    active = models.BooleanField(default=True)
```

and configuration beneath that:

```text
PricingPlan
    StandardRateConfig
    EarlyBirdConfig
    NightOwlConfig
    VehicleMultiplierConfig
    LoyaltyDiscountConfig
```

For example:

```python
class VehicleMultiplier(models.Model):
    pricing_plan = models.ForeignKey(PricingPlan, ...)
    vehicle_type = models.CharField(...)
    multiplier = models.DecimalField(max_digits=5, decimal_places=2)
```

This solves a subtle historical problem: if management changes the car hourly rate from `$5/$3/$2` to `$6/$4/$2.50` tomorrow, you **shouldn't overwrite today's rates**. You publish a new pricing plan with a new `valid_from`.

### Public holidays deserve a model

The requirements define weekdays as Monday–Friday **excluding public holidays**.

So I'd have:

```python
class PublicHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=128)
```

Unless you're obtaining them from some authoritative external service.

That gives your pricing code a straightforward:

```python
is_weekday = (
    entered_at.weekday() < 5
    and not PublicHoliday.objects.filter(date=entered_at.date()).exists()
)
```

though I'd cache/fetch the holidays outside the actual calculation loop.

### What I would *not* model

I wouldn't make tables like:

```text
PeakHourWindow
EarlyBirdWindow
NightOwlWindow
HourlyBracket
Rule
Condition
Operator
RuleArgument
```

and try to build a generic pricing-rule DSL in SQL.

You *can*, but it turns a relatively clean domain into a home-grown rules engine.

For example, Night Owl isn't merely:

```text
entry >= 18:00
exit < 10:00
```

It specifically requires the exit to occur on the **next consecutive calendar day**, and the specification separately invalidates both specials for stays over 24 hours.

That's business logic, and Python expresses it much more clearly:

```python
class NightOwlPolicy:
    def is_applicable(self, session):
        ...
```

rather than turning it into generic database rules.

So architecturally I'd end up with:

```text
DATABASE                           DOMAIN CODE

Customer
Vehicle                       ┌── StandardHourlyPolicy
ParkingSpot                   ├── EarlyBirdPolicy
ParkingSession ──────────────>├── NightOwlPolicy
PricingPlan                   │
PublicHoliday                 └── RateCalculator
RateEvaluation                       │
      ↑                              │
      └──────────────────────────────┘
               persists results
```

The `RateCalculator` itself can then be almost trivial:

```python
class RateCalculator:
    policies = [
        StandardHourlyPolicy(),
        EarlyBirdPolicy(),
        NightOwlPolicy(),
    ]

    def calculate(self, session):
        evaluations = [
            policy.evaluate(session)
            for policy in self.policies
        ]

        applicable = [
            result
            for result in evaluations
            if result.applicable
        ]

        return min(applicable, key=lambda x: x.amount)
```

That's the model I'd favour: **relational data for things and historical facts; Python classes for pricing behaviour; `RateEvaluation` as the bridge between the two.** It also leaves you room to version the pricing configuration later without designing an elaborate generic rules engine upfront.

--------------

>> Briefly: Expand on RateEvaluation

`RateEvaluation` is the **result of running one pricing policy against one parking session**.

So for a single session you might store:

```text
Standard Hourly → applicable, $42.50
Early Bird      → applicable, $15.00
Night Owl       → not applicable
```

Each of those rows is a `RateEvaluation`. Then the system picks the cheapest applicable one — here, Early Bird.

It’s mainly useful as an **audit/debug record**: it tells you which policies were considered, whether they applied, what amount each produced, and optionally how that amount was calculated.

---------------

>> Store the time intervals in the db by using postgres datetime ranges

For recurring daily windows like `07:00–10:00` and `16:00–19:00`, I’d prefer PostgreSQL **range types**.

For example, `timerange` doesn’t exist natively, but you can model daily windows as either:

```python
start_time = models.TimeField()
end_time = models.TimeField()
```

or use PostgreSQL `int4range` with “minutes since midnight”:

```text
[420, 600)    # 07:00–10:00
[960, 1140)   # 16:00–19:00
```

That maps nicely to the inclusive-start/exclusive-end semantics in your requirements.

`tsrange`/`tstzrange` are better when the interval represents **specific absolute datetimes**, e.g. `[2026-09-28 07:00, 2026-09-28 10:00)`, not a repeating daily rule.

So: **daily recurring rules → start/end or numeric range; concrete calendar intervals → PostgreSQL timestamp ranges; bitmask only if your time granularity is deliberately fixed.**

---------------
