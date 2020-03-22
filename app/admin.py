from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.HouseholdAppliance)
admin.site.register(models.Address)
admin.site.register(models.Measure)