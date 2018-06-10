from django.apps import AppConfig
from django_cron import CronJobBase, Schedule
<<<<<<< HEAD
from .models import Sensor, Owner, SensorValue
=======
from .models import Sensor, Owner
>>>>>>> f9d55104e879fdd03d9145ef30b49de67f006b51
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

<<<<<<< HEAD
        ownerLDI, created = Owner.objects.get_or_create(name='LufdatenInfo', idNumber=int(3))
        if created:
            ownerLDI.save()
=======
        ownerLDI = Owner.objects.get_or_create(name='LufdateInfo', idNumber=int(3))
        ownerLDI.save()
>>>>>>> f9d55104e879fdd03d9145ef30b49de67f006b51
        print(ownerLDI)
        for sensorData in data:

            sensorModel, created = Sensor.objects.get_or_create(
<<<<<<< HEAD
                owner_id= 1,
                name = str(sensorData['id']),
                idNumber = int(sensorData['id']),
=======
                owner_id= 2,
                name = str(sensorData['id']),
                idNumber = int(sensorData['id']),
                value = float(0.0),
>>>>>>> f9d55104e879fdd03d9145ef30b49de67f006b51
                latitude = float(sensorData['location']['latitude']),
                longitude = float(sensorData['location']['longitude']),
                location = 'None'
                )
<<<<<<< HEAD

            if created:
                sensorModel.save()
            valueFromJson = float(sensorData['sensordatavalues'][0]['value'])
            timestepData, created = SensorValue.objects.get_or_create(sensor_id = sensorModel.id,value = valueFromJson)
            if created:
                timestepData.save()
            print(sensorData)
=======
            print(sensorData)
            sensorModel.save()
>>>>>>> f9d55104e879fdd03d9145ef30b49de67f006b51
