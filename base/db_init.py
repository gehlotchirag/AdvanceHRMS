"""
Database initialization / demo-load eligibility checks.
"""

from employee.models import Employee
from horilla_auth.models import HorillaUser


def initialize_database_condition():
    """
    True if the DB should show init / load-demo UI: no users, or every superuser lacks an Employee.
    """
    init_database = not HorillaUser.objects.exists()
    if not init_database:
        init_database = True
        superusers = HorillaUser.objects.filter(is_superuser=True)
        for user in superusers:
            if Employee.objects.filter(employee_user_id=user).exists():
                init_database = False
                break
    return init_database
