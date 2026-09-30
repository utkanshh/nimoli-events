from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a staff organizer account for the Nimoli Bhandari Events dashboard."

    def handle(self, *args, **options):
        User = get_user_model()
        username = input("Username: ").strip()
        if not username:
            raise CommandError("Username cannot be blank.")
        if User.objects.filter(username__iexact=username).exists():
            raise CommandError(f"An account named '{username}' already exists.")

        password = getpass("Password (input hidden): ")
        confirmation = getpass("Password again: ")
        if not password:
            raise CommandError("Password cannot be blank.")
        if password != confirmation:
            raise CommandError("The passwords did not match. No account was created.")

        user = User(username=username, is_staff=True)
        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            raise CommandError("; ".join(exc.messages)) from exc

        user.set_password(password)
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Organizer '{username}' created. Sign in at /accounts/login/."
            )
        )
