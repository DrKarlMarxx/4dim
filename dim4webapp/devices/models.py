from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils import timezone
from django.contrib.gis.db import models as gisModels
from django.db.models import Manager as GeoManager

# Create your models here.


class Owner(models.Model):
    name = models.CharField(max_length=200)
    idNumber = models.IntegerField()
    def __str__(self):
        return self.name


class Sensor(gisModels.Model):
    owner = gisModels.ForeignKey(Owner, on_delete=models.CASCADE)
    location_number = gisModels.CharField(max_length=200)
    ldi_number = gisModels.BigIntegerField(max_length=200)
    geom = gisModels.PointField(srid=4326)
    location = gisModels.CharField(max_length=200)
    objects = GeoManager()
    longitude = gisModels.FloatField()
    latitude = gisModels.FloatField()
    clusterNumber = gisModels.IntegerField(default=0)

    def __repr__(self):
        return 'ldi_number' + str(self.ldi_number)





    def __str__(self):
        return self.name




class SensorValue(TimeStampedModel):

    created = models.DateTimeField(default=timezone.now())
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.FloatField()
    type = models.CharField(max_length=100)

class CurrentSensorValue(TimeStampedModel):

    created = models.DateTimeField(default=timezone.now())
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.FloatField()
    type = models.CharField(max_length=100)


class WeatherData(TimeStampedModel):

    created = models.DateTimeField(default=timezone.now())
    sensorvalue = models.ForeignKey(SensorValue, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    wind_speed = models.FloatField()
    wind_deg = models.FloatField()
    rain = models.FloatField()
    clouds = models.FloatField()
    name = models.CharField(max_length=100)


