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
    name = gisModels.CharField(max_length=200)
    idNumber = gisModels.IntegerField()
    geom = gisModels.PointField()
    location = gisModels.CharField(max_length=200)
    objects = GeoManager()
    longitude = gisModels.FloatField()
    latitude = gisModels.FloatField()





    def __str__(self):
        return self.name




class SensorValue(TimeStampedModel):

    created = models.DateTimeField(default=timezone.now())
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.FloatField()


