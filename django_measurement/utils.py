import decimal
from typing import Type

from measurement.base import AbstractMeasure


def get_measurement(
    measure: Type[AbstractMeasure], value: decimal.Decimal
) -> AbstractMeasure:
    unit = next(iter(measure.get_base_unit_names(measure)))
    return measure(f"{value} {unit}")
