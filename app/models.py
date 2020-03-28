from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="address", on_delete=models.DO_NOTHING)
    street = models.TextField()
    number = models.IntegerField()
    complement = models.TextField(blank=True, null=True)
    neighborhood = models.TextField()
    city = models.TextField()
    state = models.TextField()
    energy_company = models.TextField(blank=True, null=True)


class HouseholdAppliance(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="household_appliance", on_delete=models.CASCADE)
    type = models.TextField(blank=True, null=True)
    model = models.TextField(blank=True, null=True)
    energy_consumption = models.TextField(blank=True, null=True)
    classification = models.CharField(max_length=1)
    brand = models.TextField(blank=True, null=True)
    purchased_at = models.DateField()


class Measure(models.Model):
    household_appliance = models.ForeignKey(HouseholdAppliance, related_name="household_appliance", on_delete=models.DO_NOTHING)
    voltage = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    current = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    active_power = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    energy = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    frequency = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    power_factor = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)



