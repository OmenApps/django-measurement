import decimal
from functools import lru_cache
from typing import Type

from django.conf import settings
from django.db import connection

from measurement.base import AbstractMeasure


def get_measurement(measure: Type[AbstractMeasure], value: decimal.Decimal) -> AbstractMeasure:
    unit = next(iter(measure.get_base_unit_names()))
    return measure(f"{value} {unit}")


@lru_cache
def is_postgres():
    """Returns True if the DB ENGINE setting is postgresql"""

    postgresql_engines = [
        "django.db.backends.postgresql",
        "django.contrib.gis.db.backends.postgis",
    ]

    if hasattr(settings, "MEASUREMENTS_CUSTOM_POSTGRESQL_ENGINE"):
        # Makes it possible for user to indicate that their custom
        # engine makes use of PostgreSQL
        postgresql_engines += [getattr(settings, "MEASUREMENTS_CUSTOM_POSTGRESQL_ENGINE")]

    if connection.settings_dict["ENGINE"] in postgresql_engines:
        return True
    return False
