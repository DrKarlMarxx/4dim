# Register your models here.
from django.contrib.gis import admin

from .models import Owner, Sensor,SensorValue



class MyClassAdmin(admin.GeoModelAdmin):
    readonly_fields = ('created', 'modified', 'geom')


admin.site.register(Owner)
admin.site.register(Sensor,admin.GeoModelAdmin)
admin.site.register(SensorValue,admin.GeoModelAdmin)