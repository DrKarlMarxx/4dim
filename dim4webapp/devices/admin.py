from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Owner, Sensor

admin.site.register(Owner)
admin.site.register(Sensor)