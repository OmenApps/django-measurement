from django import forms

from django_measurement.forms import MeasurementSelectField
from tests.models import MeasurementTestModel

from measurement.measures import Area, Distance, Volume, VolumetricFlowRate


class MeasurementTestForm(forms.ModelForm):
    class Meta:
        model = MeasurementTestModel
        exclude = []


class FeaturesTestForm(forms.Form):
    simple = MeasurementSelectField(VolumetricFlowRate)


class AbstractMeasureTestForm(forms.Form):
    simple = MeasurementSelectField(Distance)


class TwoFactorTestForm(forms.Form):
    simple = MeasurementSelectField(Area)


class ThreeFactorTestForm(forms.Form):
    simple = MeasurementSelectField(Volume)


class FractionMeasureBaseTestForm(forms.Form):
    simple = MeasurementSelectField(VolumetricFlowRate)
