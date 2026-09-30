from django.core.management.base import BaseCommand
from django.db.models import Q

from guests.models import Guest


SAMPLE_GUESTS = (
    ("Priya Sharma", "+91 90000 00001"),
    ("Oliver Bennett", "+44 7700 900001"),
    ("Meera Kapoor", "+91 90000 00002"),
    ("Luca Moretti", "+39 312 345 6780"),
    ("Ananya Iyer", "+91 90000 00003"),
    ("Sofia Laurent", "+33 6 12 34 56 70"),
    ("Arjun Mehta", "+91 90000 00004"),
)


class Command(BaseCommand):
    help = "Remove only the exact fictional guests shipped as demo samples."

    def handle(self, *args, **options):
        sample_filter = Q(pk__in=[])
        for name, phone in SAMPLE_GUESTS:
            sample_filter |= Q(name=name, phone=phone)
        deleted, _ = Guest.objects.filter(sample_filter).delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {deleted} fictional demo records."))
