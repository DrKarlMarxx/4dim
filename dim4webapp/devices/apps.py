from django.apps import AppConfig
from django_cron import CronJobBase, Schedule
from .models import Sensor, Owner, SensorValue, WeatherData, CurrentSensorValue
import json
import urllib.request
from django.contrib.gis.geos import Point
import asyncio
import websockets as ws
from django.utils import timezone
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
import pywt
import datetime
import pandas as pd



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

        usedIDSet = set()
        for sensorData in data:

            sensorLatitude = sensorData['location']['latitude']
            sensorLongitude = sensorData['location']['longitude']




            currentSensor = Sensor.objects.filter(ldi_number=int(sensorData['sensor']['id']))

            type_selection = [d['value_type'] for d in sensorData['sensordatavalues'][:]] == "P1"

            if currentSensor.count()==0:
                print('new')
                print(int(sensorData['id']))
                sensorModel, created = Sensor.objects.get_or_create(
                    owner_id= ownerLDI.id,
                    location_number = str(sensorData['location']['id']),
                    ldi_number = int(sensorData['sensor']['id']),
                    geom = Point(float(sensorData['location']['longitude']),float(sensorData['location']['latitude'])),
                    location = 'Empty',
                    longitude = float(sensorData['location']['longitude']),
                    latitude = float(sensorData['location']['latitude']),
                    )

                geoNamesRequestUrl = r'http://api.geonames.org/findNearbyJSON?lat='+str(sensorLatitude)+'&lng='+str(sensorLongitude)+'&username=DrKarlMarxx'
                try:
                    with urllib.request.urlopen(geoNamesRequestUrl) as urlJson:
                        geoNamesData = json.loads(urlJson.read())
                    sensorModel.location = geoNamesData["geonames"][0]["toponymName"]
                except:
                    pass
                sensorModel.save()
            else:
                sensorModel =currentSensor[0]
            if sensorModel.id not in usedIDSet:
                for sensorvalueList in sensorData['sensordatavalues'][:]:
                    typeFromJson = str(sensorvalueList['value_type'])
                    valueFromJson = float(sensorvalueList['value'])
                    timestepData = SensorValue(sensor_id = sensorModel.id,value = valueFromJson,type = typeFromJson)
                    timestepData.save()
                    runningCurrentSensorValue = CurrentSensorValue.objects.filter(sensor_id=sensorModel.id)
                    if runningCurrentSensorValue.count()==0:
                        currentSensorValue, created = CurrentSensorValue.objects.get_or_create(sensor_id = sensorModel.id,value = valueFromJson,type = typeFromJson)
                    else:
                        currentSensorValue = runningCurrentSensorValue[0]
                        currentSensorValue.value = valueFromJson
                    currentSensorValue.save()
                    


                """
                weatherDataRequestUrl = r'api.openweathermap.org/data/2.5/weather?lat='+str(sensorLatitude)+'&lon='+str(sensorLongitude)
                with urllib.request.urlopen(weatherDataRequestUrl) as urlJson:
                    weatherData = json.loads(urlJson.read())

                weatherData, created = WeatherData.objects.get_or_create(sensorvalue_id=timestepData.id,
                                                                         temperature=weatherData['main']['temp'],
                                                                            humidity = weatherData['main']['humidity'],
                                                                            pressure = weatherData['main']['pressure'],
                                                                            temp_min = weatherData['main']['temp_min'],
                                                                            temp_max = weatherData['main']['temp_max'],
                                                                            wind_speed = weatherData['wind']['speed'],
                                                                            wind_deg = weatherData['wind']['deg'],
                                                                            rain = weatherData['rain']['3h'],
                                                                            clouds = weatherData['clouds']['all'],
                                                                            name = weatherData['name'])
                """
                usedIDSet.add(sensorModel.id)

        for savedSensorValue in SensorValue._meta.get_fields():
            if (timezone.now()-savedSensorValue.created).days >= 7:
                savedSensorValue.delete()






class ReadFromLoriotWebSocket(CronJobBase):
    RUN_EVERY_MINS = 5 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dim4webapp.readFromLoriotWebSocket'    # a unique code

    def do(self):
        async def test():
            data = {}
            data['EUI'] = 'default'
            while data['EUI'][-2:] != '45':
                async with ws.connect(r'wss://eu1.loriot.io/app?token=vnoTPgAAAA1ldTEubG9yaW90LmlvioIq8UeQhDkDJ-VVtrbZNQ==') as websocket:

                    await websocket.send('hello')
                    response = await websocket.recv()
                    data = json.loads(response)

            ownerLDI, created = Owner.objects.get_or_create(name='Andrin Battaglia', idNumber=int(2))
            if created:
                ownerLDI.save()

            currentSensor = Sensor.objects.filter(ldi_number=int(data['EUI'], 16))
            if len(data['data'])>8 and currentSensor.count()==0:
                sensorLatitude = (int(data['data'][8:10], 16) * 256**3 +int(data['data'][10:12], 16) * 256**2 +int(data['data'][12:14], 16) * 256 + int(data['data'][14:16], 16)-2147483648) / 1000000
                sensorLongitude =  (int(data['data'][16:18], 16) * 256**3 +int(data['data'][18:20], 16) * 256**2 +int(data['data'][20:22], 16) * 256 + int(data['data'][22:24], 16)-2147483648) / 1000000




                sensorModel, created = Sensor.objects.get_or_create(
                    owner_id= ownerLDI.id,
                    location_number = 0,
                    ldi_number = int(data['EUI'],16),
                    geom = Point(float(sensorLongitude),float(sensorLatitude)),
                    location = 'Empty',
                    longitude = float(sensorLongitude),
                    latitude = float(sensorLatitude),
                    )

                geoNamesRequestUrl = r'http://api.geonames.org/findNearbyJSON?lat='+str(sensorLatitude)+'&lng='+str(sensorLongitude)+'&username=DrKarlMarxx'
                try:
                    with urllib.request.urlopen(geoNamesRequestUrl) as urlJson:
                        geoNamesData = json.loads(urlJson.read())
                    sensorModel.location = geoNamesData["geonames"][0]["toponymName"]
                except:
                    pass
                sensorModel.save()
            elif len(data['data'])>8 and currentSensor.count()==1:
                sensorLatitude = (int(data['data'][8:10], 16) * 256 ** 3 + int(data['data'][10:12],
                                                                               16) * 256 ** 2 + int(data['data'][12:14],
                                                                                                    16) * 256 + int(
                    data['data'][14:16], 16) - 2147483648) / 1000000
                sensorLongitude = (int(data['data'][16:18], 16) * 256 ** 3 + int(data['data'][18:20],
                                                                                 16) * 256 ** 2 + int(
                    data['data'][20:22], 16) * 256 + int(data['data'][22:24], 16) - 2147483648) / 1000000

                sensorModel = currentSensor[0]
                sensorModel.geom = Point(float(sensorLongitude),float(sensorLatitude))
                sensorModel.longitude = float(sensorLongitude)
                sensorModel.latitude = float(sensorLatitude)
                sensorModel.save()
            else:
                sensorModel = currentSensor[0]

            if sensorModel:

                PM10 = (int(data['data'][0:2], 16) * 256 + int(data['data'][2:4], 16)) / 100
                PM25 = (int(data['data'][4:6], 16) * 256 + int(data['data'][6:8], 16)) / 100
                timestepData, created = SensorValue.objects.get_or_create(sensor_id=sensorModel.id, value=PM10, type='P1')

                if created:
                    timestepData.save()
                timestepData, created = SensorValue.objects.get_or_create(sensor_id=sensorModel.id, value=PM25, type='P2')
                if created:
                    timestepData.save()


                currentSensorValue, created = CurrentSensorValue.objects.get_or_create(sensor_id=sensorModel.id,
                                                                                       value=PM10,
                                                                                       type='P1')
                currentSensorValue.save()
                currentSensorValue, created = CurrentSensorValue.objects.get_or_create(sensor_id=sensorModel.id,
                                                                                       value=PM25,
                                                                                       type='P2')
                currentSensorValue.save()

        asyncio.get_event_loop().run_until_complete(test())

        for savedSensorValue in SensorValue._meta.get_fields():
            if (timezone.now()-savedSensorValue.Created).days > 7:
                savedSensorValue.delete()


if __name__ == "__main__":
    test = ReadFromLuftdateInfoJSON()
    thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))