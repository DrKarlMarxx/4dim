from django.contrib import admin

# Register your models here.
from django.contrib.gis import admin
from .models import Place




admin.site.register(Place, admin.OSMGeoAdmin)