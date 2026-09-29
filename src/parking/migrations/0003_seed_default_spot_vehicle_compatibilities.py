"""Seed default compatibility facts for built-in spot and vehicle types."""

from django.db import migrations


DEFAULT_COMPATIBILITIES = (
    ("compact", "motorcycle"),
    ("compact", "car"),
    ("large", "bus"),
)


def seed_default_compatibilities(apps, schema_editor):
    compatibility_model = apps.get_model("parking", "SpotTypeVehicleCompatibility")
    for spot_type, vehicle_type in DEFAULT_COMPATIBILITIES:
        compatibility_model.objects.get_or_create(
            spot_type=spot_type,
            vehicle_type=vehicle_type,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("parking", "0002_publicholiday_parkingsession_rateevaluation_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_default_compatibilities, migrations.RunPython.noop),
    ]
