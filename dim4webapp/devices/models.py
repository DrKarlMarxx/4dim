from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils import timezone
# Create your models here.


class Owner(models.Model):
    name = models.CharField(max_length=200)
    idNumber = models.IntegerField()
    def __str__(self):
        return self.name


class Sensor(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    idNumber = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=100)
    objects = models.Manager()




    def __str__(self):
        return self.name




class SensorValue(TimeStampedModel):

    created = models.DateTimeField(default=timezone.now())
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.FloatField()


