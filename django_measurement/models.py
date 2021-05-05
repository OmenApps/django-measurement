import copy
import decimal
import logging
from typing import Type

from django.db import connection as db_connection
from django.db.migrations.serializer import BaseSerializer
from django.db.migrations.writer import MigrationWriter
from django.db.models import DecimalField
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from . import forms, utils, validators

from measurement.base import AbstractMeasure

logger = logging.getLogger("django_measurement")


class MeasureSerializer(BaseSerializer):
    def serialize(self):
        return (
            repr(self.value),
            {f"from measurement.measures import {type(self.value).__qualname__}"},
        )


MigrationWriter.register_serializer(AbstractMeasure, MeasureSerializer)


class MeasurementField(DecimalField):
    description = "Easily store, retrieve, and convert python measures."
    empty_strings_allowed = False
    default_error_messages = {
        "invalid_type": _("'%(value)s' (%(type_given)s) value" " must be of type %(type_wanted)s."),
    }

    def __init__(self, *args, measure: Type[AbstractMeasure] = None, **kwargs):

        self.measure = measure
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(MeasurementField, self).deconstruct()
        kwargs["measure"] = self.measure
        return name, path, args, kwargs

    def get_prep_value(self, value):
        if value is not None and isinstance(value, AbstractMeasure):
            return value.si_value
        elif value is not None and isinstance(value, decimal.Decimal):
            # Is this accurate for Volume? and other square/cubic/factors type measures?
            return self.measure(f"{value} {self.measure.get_base_unit_names()[0]}")

    def get_default_unit(self):
        return next(iter(self.measure.get_base_unit_names(measure)))

    def from_db_value(self, value, *args, **kwargs):
        if value is not None:
            return utils.get_measurement(
                measure=self.measure,
                value=value,
            )

    def value_to_string(self, obj):
        return str(self.value_from_object(obj))

    def get_db_prep_save(self, value, connection):
        value = self.to_python(value)
        if isinstance(value, AbstractMeasure):
            value = value.si_value
        if isinstance(value, int):
            value = decimal.Decimal(value)
        return connection.ops.adapt_decimalfield_value(
            value, self.max_digits, self.decimal_places
        )

    def to_python(self, value):
        return value

    def deserialize_value_from_string(self, s: str):
        return self.measure(s)

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": forms.MeasurementSelectField,
                "measure": self.measure,
                **kwargs,
            }
        )

    def db_type(self, connection):
        """
        If using PostgreSQL, we can take advantage of the arbitrary numeric db column size
        https://steve.dignam.xyz/2019/10/24/arbitrary-precision-decimal-fields/
        """
        if utils.is_postgres():
            return "numeric"
        return super().db_type(connection)

    def _check_decimal_places(self):
        if utils.is_postgres():
            return []
        return super()._check_decimal_places()

    def _check_max_digits(self):
        if utils.is_postgres():
            return []
        return super()._check_max_digits()

    def _check_decimal_places_and_max_digits(self, *args, **kwargs):
        if utils.is_postgres():
            return []
        return super()._check_decimal_places_and_max_digits(*args, **kwargs)

    @cached_property
    def validators(self):
        return [
            *self.default_validators,
            *self._validators,
            validators.MeasurementValidator(self.max_digits, self.decimal_places),
        ]
