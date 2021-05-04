from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_measurement.models import MeasurementField

from measurement import measures


class MeasurementTestModel(models.Model):

    measurement_capacitance = MeasurementField(
        measure=measures.Capacitance,
        validators=[
            MinValueValidator(measures.Capacitance(Farad=1.0)),
            MaxValueValidator(measures.Capacitance(Farad=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_current = MeasurementField(
        measure=measures.Current,
        validators=[
            MinValueValidator(measures.Current(Ampere=1.0)),
            MaxValueValidator(measures.Current(Ampere=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_resistance = MeasurementField(
        measure=measures.Resistance,
        validators=[
            MinValueValidator(measures.Resistance("1 Ω")),
            MaxValueValidator(measures.Resistance("3 Ω")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_voltage = MeasurementField(
        measure=measures.Voltage,
        validators=[
            MinValueValidator(measures.Voltage(Volt=1.0)),
            MaxValueValidator(measures.Voltage(Volt=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_inductance = MeasurementField(
        measure=measures.Inductance,
        validators=[
            MinValueValidator(measures.Inductance("1.0 Henry")),
            MaxValueValidator(measures.Inductance("3.0 H")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_electric_power = MeasurementField(
        measure=measures.ElectricPower,
        validators=[
            MinValueValidator(measures.ElectricPower(VA=1.0)),
            MaxValueValidator(measures.ElectricPower(VA=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_energy = MeasurementField(
        measure=measures.Energy,
        validators=[
            MinValueValidator(measures.Energy("1 joule")),
            MaxValueValidator(measures.Energy("3 joule")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_distance = MeasurementField(
        measure=measures.Distance,
        validators=[
            MinValueValidator(measures.Distance(Metre=1.0)),
            MaxValueValidator(measures.Distance(Meter=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_area = MeasurementField(
        measure=measures.Area,
        validators=[
            MinValueValidator(measures.Area("1 metre²")),
            MaxValueValidator(measures.Area("3 m²")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_volume = MeasurementField(
        measure=measures.Volume,
        validators=[
            MinValueValidator(measures.Volume(litre=1.0)),
            MaxValueValidator(measures.Volume("3 ℓ")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_volumetric_flow_rate = MeasurementField(
        measure=measures.VolumetricFlowRate,
        validators=[
            MinValueValidator(measures.VolumetricFlowRate("1 cumecs")),
            MaxValueValidator(measures.VolumetricFlowRate("3 CMS")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_speed = MeasurementField(
        measure=measures.Speed,
        validators=[
            MinValueValidator(measures.Speed(kph=1.0)),
            MaxValueValidator(measures.Speed(kph=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_mass = MeasurementField(
        measure=measures.Mass,
        validators=[
            MinValueValidator(measures.Mass(Gram=1.0)),
            MaxValueValidator(measures.Mass(Gram=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_pressure = MeasurementField(
        measure=measures.Pressure,
        validators=[
            MinValueValidator(measures.Pressure(pascal=1.0)),
            MaxValueValidator(measures.Pressure(pascal=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_radioactivity = MeasurementField(
        measure=measures.Radioactivity,
        validators=[
            MinValueValidator(measures.Radioactivity(Bq=1.0)),
            MaxValueValidator(measures.Radioactivity(Bq=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_temperature = MeasurementField(
        measure=measures.Temperature,
        validators=[
            MinValueValidator(measures.Temperature(Kelvin=1.0)),
            MaxValueValidator(measures.Temperature(Kelvin=3.0)),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_time = MeasurementField(
        measure=measures.Time,
        validators=[
            MinValueValidator(measures.Time("1 sec")),
            MaxValueValidator(measures.Time("3 s")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    measurement_frequency = MeasurementField(
        measure=measures.Frequency,
        validators=[
            MinValueValidator(measures.Frequency("1 Hz")),
            MaxValueValidator(measures.Frequency("3 Hertz")),
        ],
        max_digits=15,
        decimal_places=10,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.measurement
