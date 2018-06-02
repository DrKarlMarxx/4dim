from django.db import models

# Create your models here.
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point
from location_field.models.spatial import LocationField



class Place(models.Model):
    city = models.CharField(max_length=255)
    location = LocationField(based_fields=['city'], zoom=7, default=Point(1.0, 1.0))
    objects = GeoManager()
