from django.core.management.base import BaseCommand

from guests.models import Guest


class Command(BaseCommand):
    help = "Add fictional sample guests for the local prototype."

    def handle(self, *args, **options):
        sample_guests = [
            ("Priya Sharma", "+91 90000 00001", "confirmed", "two_nights"),
            ("Oliver Bennett", "+44 7700 900001", "pending", "not_selected"),
            ("Meera Kapoor", "+91 90000 00002", "confirmed", "three_nights"),
            ("Luca Moretti", "+39 312 345 6780", "declined", "not_selected"),
            ("Ananya Iyer", "+91 90000 00003", "pending", "not_selected"),
            ("Sofia Laurent", "+33 6 12 34 56 70", "confirmed", "two_nights"),
            ("Arjun Mehta", "+91 90000 00004", "confirmed", "one_night"),
        ]
        created = 0
        for name, phone, status, hotel in sample_guests:
            _, was_created = Guest.objects.get_or_create(
                phone=phone,
                defaults={
                    "name": name,
                    "rsvp_status": status,
                    "hotel_status": hotel,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Added {created} fictional sample guests."))
