"""
Load demo fixtures without using the web UI (avoids HTTP / proxy timeouts on Railway).

Usage (from project root, with env vars loaded):

  railway run python manage.py load_horilla_demo --password "$DB_INIT_PASSWORD"

Or locally:

  python manage.py load_horilla_demo --password "your-db-init-password"
"""

from os import path

from django.conf import settings
from django.core.management import BaseCommand, call_command

from base.db_init import initialize_database_condition
from base.demo_fixtures import demo_fixture_filenames


class Command(BaseCommand):
    help = "Load Horilla demo data (same fixtures as Login → Load Demo Data)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            required=True,
            help="Must match DB_INIT_PASSWORD / settings.DB_INIT_PASSWORD",
        )

    def handle(self, *args, **options):
        pwd = options["password"]
        if pwd != settings.DB_INIT_PASSWORD:
            self.stderr.write(self.style.ERROR("Invalid password (DB_INIT_PASSWORD mismatch)."))
            raise SystemExit(1)
        if not initialize_database_condition():
            self.stderr.write(
                self.style.ERROR(
                    "Database is not in demo-load state (e.g. a superuser with an employee "
                    "already exists). Use a fresh DB or adjust data before loading."
                )
            )
            raise SystemExit(1)
        fixture_paths = [
            path.join(settings.BASE_DIR, "load_data", f) for f in demo_fixture_filenames()
        ]
        self.stdout.write(f"Loading {len(fixture_paths)} fixture file(s)...")
        call_command("loaddata", *fixture_paths, verbosity=1)
        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully."))
