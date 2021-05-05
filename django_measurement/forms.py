import logging
from decimal import ROUND_HALF_UP, Decimal, DecimalException
from typing import Type

from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection
from django.template import loader
from django.utils import formats
from django.utils.safestring import mark_safe

from django_measurement.validators import MeasurementValidator

from .utils import get_measurement, is_postgres

from measurement.base import AbstractMeasure

logger = logging.getLogger("django_measurement")


class MeasurementSelectWidget(forms.MultiWidget):
    template_name = "measurement_select_widget.html"

    def __init__(
        self,
        measure: Type[AbstractMeasure] = None,
        unit_choices: tuple = None,
        unit_primary: str = None,
        max_digits: int = None,
        decimal_places: int = None,
        max_trailing_digits: int = None,
        normalize: bool = False,
        show_table: bool = False,
        decimal_widget=None,
        unit_choices_widget=None,
        attrs=None,
        *args,
        **kwargs,
    ):
        self.measure: Type[AbstractMeasure] = measure
        self.max_trailing_digits = max_trailing_digits
        self.normalize = normalize  # https://docs.python.org/3/library/decimal.html#decimal.Decimal.normalize
        self.show_table = show_table

        self.unit_primary = unit_primary

        # If unit_primary is in unit_choices, move it to front of unit_choices
        self.unit_choices = self.move_unit_primary_to_front(unit_choices, unit_primary)

        # Allow end user to override widgets, for instance to use RadioSelect rather than Select
        if decimal_widget is not None:
            decimal_widget = forms.TextInput(attrs=attrs)
        if unit_choices_widget is not None:
            unit_choices_widget = forms.Select(attrs=attrs, choices=self.unit_choices)

        widgets = [decimal_widget, unit_choices_widget]
        super().__init__(widgets, *args, **kwargs)

    def move_unit_primary_to_front(self, unit_choices, unit_primary):
        """
        Checks if unit_primary is in any of the sublists in unit_choices, and
        if so, moves that sublist to the front of unit_choices.
        """
        unit_primary_sublist = None
        unit_choices_list = list(unit_choices)

        for sublist in unit_choices:
            if sublist[0] == unit_primary or (
                unit_primary is not None and sublist[0] == unit_primary.replace("_", " ")
            ):
                unit_primary_sublist = sublist
                break

        if unit_primary_sublist is not None:
            try:
                if unit_primary_sublist is not None:
                    unit_choices_list.remove(unit_primary_sublist)
            except:
                pass

            try:
                if unit_primary_sublist is not None:
                    unit_primary_sublist[0] = unit_primary_sublist[0].replace("_", " ")
                    unit_choices_list.remove(unit_primary_sublist)
            except:
                pass

            unit_choices_list.insert(0, unit_primary_sublist)
        else:
            self.unit_choices = unit_choices

        return unit_choices_list

    def get_unit(self, value):
        unit = None
        choice_units = set([u for u, n in self.unit_choices])

        if self.unit_primary is not None:
            unit = self.unit_primary

            if unit not in choice_units:
                unit = choice_units.pop()
        elif value is not None:
            # default to the base_unit
            unit = next((i for i in value.get_base_unit_names() if i in choice_units), None)

        if not unit:
            unit = choice_units.pop()

        return unit

    def decompress(self, value):

        if value is not None:
            unit = self.get_unit(value)
            magnitude = getattr(value, unit)
            return [magnitude, unit]

        return [None, None]

    def get_context(self, name, value, attrs):
        """Add table of unit conversions to context."""

        context = super().get_context(name, value, attrs)

        if value is not None and type(value) is list:
            try:
                dec_value = Decimal(str(value[0]))
            except DecimalException:
                raise ValidationError("Invalid decimal input", code="invalid")

        # Add context for the values table
        if self.show_table:
            context["values_list"] = self.create_table(value)

        return context

    def create_table(self, value):
        values_list = []
        for choice in self.unit_choices:
            unit_output, unit_display = choice
            if value is not None:
                if isinstance(value, self.measure):
                    output_value = value[unit_output]
                elif isinstance(value, list):
                    output_value = self.measure(*value)[unit_output]
                else:
                    raise ImproperlyConfigured("Incorrect value type in get_context of MeasurementSelectWidget")
                # Clean up representation if desired
                if self.max_trailing_digits is not None:
                    trailing = "".zfill(self.max_trailing_digits)
                    output_value = output_value.quantize(Decimal(f".{trailing}"))
                if self.normalize:
                    output_value = output_value.normalize()
            else:
                output_value = 0
            values_list.append([unit_display, output_value])
        return values_list


class MeasurementSelectField(forms.MultiValueField):
    """
    A django form field used to allow input of a value and selection of a measurement unit.
    """

    def __init__(
        self,
        measure: Type[AbstractMeasure] = None,
        unit_choices: tuple = None,
        unit_primary: str = None,
        max_digits: int = None,
        decimal_places: int = None,
        max_trailing_digits: int = None,
        normalize: bool = False,
        show_table: bool = False,
        max_value: Type[AbstractMeasure] = None,
        min_value: Type[AbstractMeasure] = None,
        validators=None,
        attrs=None,
        *args,
        **kwargs,
    ):
        """
        Constructs all the necessary attributes for the MeasurementSelectField.

        Parameters
        ----------
            measure : Type[AbstractMeasure]
                the measure class to be used, such as Time, Volume, etc
            unit_choices (optional) : tuple
                a tuple of two-tuples, representing the allowed choices to limit selection (and the values table) to.
                If not provided, all possible variants for the given measure are shown.
            unit_primary : str
                a string representation of one of the unit_choices. If invalid or not provided, the primary unit for
                the given measure type will be displayed.
            max_trailing_digits (optional): int
                minimum digits to show in values in the values table
            normalize : bool
                remove lagging zeroes in display
            show_table : bool
                show the measurements table of values in the MeasurementSelectWidget
            max_value : Type[AbstractMeasure] instance
                specifies the maximum allowed measurement value for this field. For instance:
                `max_value=Volume('10.999999 cubic_m')`
            min_value : Type[AbstractMeasure] instance
                specifies the minimum allowed measurement value for this field. For instance:
                `min_value=Volume('0.999999 cubic_m')`
            validators : validator
                additional validators

            attrs : *
                attributes to be passed to
            decimal_widget (optional) : django form widget
                allows substitution of a different widget. Defaut used is TextInput
            unit_choices_widget (optional) : django form widget
                allows substitution of a different widget. Defaut used is Select
        """

        self.measure: Type[AbstractMeasure] = measure

        if not unit_choices:
            unit_choices = tuple(((u, getattr(measure, "LABELS", {}).get(u, u)) for u in measure._units))

        if validators is None:
            validators = []

        if min_value is not None:
            if not isinstance(min_value, AbstractMeasure):
                msg = '"min_value" must be a measure, got %s' % type(min_value)
                raise ValueError(msg)
            validators += [MinValueValidator(min_value)]

        if max_value is not None:
            if not isinstance(max_value, AbstractMeasure):
                msg = '"max_value" must be a measure, got %s' % type(max_value)
                raise ValueError(msg)
            validators += [MaxValueValidator(max_value)]

        decimal_field = forms.DecimalField(*args, **kwargs)
        choice_field = forms.ChoiceField(choices=unit_choices)
        defaults = {
            "widget": MeasurementSelectWidget(
                decimal_widget=decimal_field.widget,
                unit_choices_widget=choice_field.widget,
                unit_choices=unit_choices,
                unit_primary=unit_primary,
                measure=measure,
                max_trailing_digits=max_trailing_digits,
                normalize=normalize,
                show_table=show_table,
                attrs=attrs,
            ),
        }
        defaults.update(kwargs)
        fields = (decimal_field, choice_field)

        super().__init__(fields, validators=validators, *args, **defaults)

    def compress(self, data_list):
        if not data_list:
            return None

        value, unit = data_list
        if value in self.empty_values:
            return None

        try:
            value = Decimal(str(value))
        except DecimalException:
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        orig_measure = self.measure(f"{value} {unit}")

        # If we are not using Postgresql:
        # Need to ensure the value which will be saved in DB meets the
        # digit & decimal requirements. So we convert to base unit,
        # and then quantize to the decimal/digit limits

        # QUESTION: Should this happen in the model field? Both?
        # QUESTION: Is this even needed? If not PostgreSQL,
        #           doesn't the db truncate the value on its own?
        if not is_postgres():
            # Get the base unit and resulting value
            base_unit = orig_measure.base_unit_names[0]
            base_value = orig_measure[base_unit]

            # Then convert back to a measure
            return self.measure(f"{base_value} {base_unit}")

        return orig_measure
