from django.apps import AppConfig
from django_cron import CronJobBase, Schedule
from .models import Sensor, Owner, SensorValue
import json
import urllib.request
from django.contrib.gis.geos import Point
import asyncio
import websockets as ws

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

        ownerLDI, created = Owner.objects.get_or_create(name='LufdatenInfo', idNumber=int(1))
        if created:
            ownerLDI.save()
        print(ownerLDI)
        for sensorData in data:

            sensorLatitude = sensorData['location']['latitude']
            sensorLongitude = sensorData['location']['longitude']






            sensorModel, created = Sensor.objects.get_or_create(
                owner_id= ownerLDI.id,
                name = str(sensorData['id']),
                idNumber = int(sensorData['id']),
                geom = Point(float(sensorData['location']['longitude']),float(sensorData['location']['latitude'])),
                location = 'Empty',
                longitude = float(sensorData['location']['longitude']),
                latitude = float(sensorData['location']['latitude'])

                )

            if created:
                geoNamesRequestUrl = r'http://api.geonames.org/findNearbyJSON?lat='+str(sensorLatitude)+'&lng='+str(sensorLongitude)+'&username=DrKarlMarxx'
                with urllib.request.urlopen(geoNamesRequestUrl) as urlJson:
                    geoNamesData = json.loads(urlJson.read())
                sensorModel.location = geoNamesData["geonames"][0]["toponymName"]
                sensorModel.save()
                print(sensorModel.geom)
            valueFromJson = float(sensorData['sensordatavalues'][0]['value'])
            timestepData, created = SensorValue.objects.get_or_create(sensor_id = sensorModel.id,value = valueFromJson)
            if created:
                timestepData.save()

        for savedSensorValue in SensorValue._meta.get_fields():
            if (timezone.now()-savedSensorValue.Created).days > 7:
                savedSensorValue.delete()


class ReadFromLoriotWebSocket(CronJobBase):
    RUN_EVERY_MINS = 5 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dim4webapp.readFromLoriotWebSocket'    # a unique code

    def do(self):
        async def test():
            async with ws.connect(r'wss://eu1.loriot.io/app?token=vnoTPgAAAA1ldTEubG9yaW90LmlvioIq8UeQhDkDJ-VVtrbZNQ==') as websocket:
                await websocket.send('hello')
                response = await websocket.recv()
                data = json.loads(response)

            ownerLDI, created = Owner.objects.get_or_create(name='Andrin', idNumber=int(1))
            if created:
                ownerLDI.save()



            sensorLatitude = '47.494098'
            sensorLongitude = '8.731144'






            sensorModel, created = Sensor.objects.get_or_create(
                owner_id= ownerLDI.id,
                name = str(data['EUI']),
                idNumber = int(0),
                geom = Point(8.731144,47.494098),
                location = 'Empty',
                longitude = 8.731144,
                latitude = 47.494098

                )

            if created:
                geoNamesRequestUrl = r'http://api.geonames.org/findNearbyJSON?lat='+str(sensorLatitude)+'&lng='+str(sensorLongitude)+'&username=DrKarlMarxx'
                with urllib.request.urlopen(geoNamesRequestUrl) as urlJson:
                    geoNamesData = json.loads(urlJson.read())
                sensorModel.location = geoNamesData["geonames"][0]["toponymName"]
                sensorModel.save()
                print(sensorModel.geom)
            valueFromJson = float(data['value'])
            timestepData, created = SensorValue.objects.get_or_create(sensor_id = sensorModel.id,value = valueFromJson)
            if created:
                timestepData.save()

        asyncio.get_event_loop().run_until_complete(test())

        for savedSensorValue in SensorValue._meta.get_fields():
            if (timezone.now()-savedSensorValue.Created).days > 7:
                savedSensorValue.delete()


