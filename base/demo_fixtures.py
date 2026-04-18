"""
Demo / load-data fixture list shared by the web UI and management commands.
"""

from __future__ import annotations

from django.apps import apps

# Order matters for foreign keys.
_BASE_FIXTURES = [
    "user_data.json",
    "employee_info_data.json",
    "base_data.json",
    "work_info_data.json",
]

_OPTIONAL_BY_APP = [
    ("attendance", "attendance_data.json"),
    ("leave", "leave_data.json"),
    ("asset", "asset_data.json"),
    ("recruitment", "recruitment_data.json"),
    ("onboarding", "onboarding_data.json"),
    ("offboarding", "offboarding_data.json"),
    ("pms", "pms_data.json"),
    ("payroll", "payroll_data.json"),
    ("payroll", "payroll_loanaccount_data.json"),
    ("project", "project_data.json"),
]


def demo_fixture_filenames() -> list[str]:
    names = list(_BASE_FIXTURES)
    names.extend(
        filename
        for app_label, filename in _OPTIONAL_BY_APP
        if apps.is_installed(app_label)
    )
    return names
