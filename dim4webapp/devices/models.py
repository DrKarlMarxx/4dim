from django.db import models

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
    value = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=100)
    def __str__(self):
        return self.name


