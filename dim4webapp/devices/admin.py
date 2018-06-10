from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Owner, Sensor,SensorValue



class MyClassAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', )


admin.site.register(Owner)
admin.site.register(Sensor)
admin.site.register(SensorValue,MyClassAdmin)