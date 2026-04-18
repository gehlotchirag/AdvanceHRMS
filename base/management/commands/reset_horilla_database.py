"""
Remove ALL rows from the database (keeps tables and migrations).

Use after a failed or partial "Load demo data" to clear duplicate-key / inconsistent state,
then run load_horilla_demo again.

Usage (with Railway env vars, including DATABASE_URL):

  railway run python manage.py reset_horilla_database --password "$DB_INIT_PASSWORD"

This calls Django's ``flush`` (same effect as ``manage.py flush --no-input``).
Session/cache (e.g. Redis) is not cleared here; sign out in the browser or wait for expiry.
"""

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Wipe all data from the database (schema unchanged). Requires DB_INIT_PASSWORD."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            required=True,
            help="Must match settings.DB_INIT_PASSWORD (same as Load Demo Data).",
        )

    def handle(self, *args, **options):
        if options["password"] != settings.DB_INIT_PASSWORD:
            self.stderr.write(self.style.ERROR("Invalid password (DB_INIT_PASSWORD mismatch)."))
            raise SystemExit(1)

        self.stdout.write(
            self.style.WARNING(
                "Flushing the database — all application data will be deleted."
            )
        )
        call_command("flush", interactive=False, verbosity=1)
        self.stdout.write(
            self.style.SUCCESS(
                "Done. You can run: python manage.py load_horilla_demo --password <same>"
            )
        )
