import uuid

from django.db import migrations, models


def populate_rsvp_tokens(apps, schema_editor):
    Guest = apps.get_model("guests", "Guest")
    for guest in Guest.objects.filter(rsvp_token__isnull=True).iterator():
        guest.rsvp_token = uuid.uuid4()
        guest.save(update_fields=["rsvp_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("guests", "0003_guest_whatsapp_opted_out_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="guest",
            name="rsvp_token",
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="guest",
            name="hotel_check_in",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="guest",
            name="hotel_check_out",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="guest",
            name="room_preference",
            field=models.CharField(
                choices=[
                    ("single", "Single room"),
                    ("double", "Double room"),
                    ("twin", "Twin room"),
                    ("none", "No room needed"),
                ],
                default="none",
                max_length=8,
            ),
        ),
        migrations.RunPython(populate_rsvp_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="guest",
            name="rsvp_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="guest",
            name="phone",
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
