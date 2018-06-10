from django.apps import AppConfig
from django_cron import CronJobBase, Schedule
from .models import Sensor, Owner
import json
import urllib.request

class DevicesConfig(AppConfig):
    name = 'devices'


class ReadFromLuftdateInfoJSON(CronJobBase):
    RUN_EVERY_MINS = 5 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dim4webapp.readFromLDIJason'    # a unique code

    def do(self):
        url = r'http://api.luftdaten.info/static/v2/data.json'
        with urllib.request.urlopen(url) as urlJson:
            data = json.loads(urlJson.read())

        ownerLDI = Owner.objects.get_or_create(name='LufdateInfo', idNumber=int(3))
        ownerLDI.save()
        print(ownerLDI)
        for sensorData in data:

            sensorModel, created = Sensor.objects.get_or_create(
                owner_id= 2,
                name = str(sensorData['id']),
                idNumber = int(sensorData['id']),
                value = float(0.0),
                latitude = float(sensorData['location']['latitude']),
                longitude = float(sensorData['location']['longitude']),
                location = 'None'
                )
            print(sensorData)
            sensorModel.save()