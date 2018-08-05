from django.apps import AppConfig
from django_cron import CronJobBase, Schedule
from .models import Sensor, Owner, SensorValue, WeatherData
import json
import urllib.request
from django.contrib.gis.geos import Point
import asyncio
import websockets as ws
from django.utils import timezone
import numpy as np
import pywt._dwt as dwt
from sklearn.cluster import DBSCAN, KMeans


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
                    timestepData, created = SensorValue.objects.get_or_create(sensor_id = sensorModel.id,value = valueFromJson,type = typeFromJson)

                    if created:
                        timestepData.save()
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
            if (timezone.now()-savedSensorValue.Created).days > 7:
                savedSensorValue.delete()


class ClusterTimeSeries(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dim4webapp.clusterTimeSeries'    # a unique code

    def do(self):
        timeSeries = []
        sensor_list=Sensor.objects.filter(owner=1)
        sensor_list_with_P1=[]
        sensor_list_with_no_cluster = []

        maxLen = 0
        for sensor in sensor_list:
            values = list(
                SensorValue.objects.filter(sensor=sensor.id, type='P1').order_by('created').values('created', 'value'))
            df = [float(d['value']) for d in values]
            if len(df)>maxLen:
                maxLen=len(df)

        for sensor in sensor_list:
            values = list(SensorValue.objects.filter(sensor=sensor.id, type='P1').order_by('created').values('created','value'))
            df = [float(d['value']) for d in values]


            try:

                (cA, cD) = dwt.dwt(df,'db2')
                if len(df)==maxLen and max(df)<500:
                    timeSeries.append(df)
                    sensor_list_with_P1.append(sensor)
                else:
                    sensor_list_with_no_cluster.append(sensor)

            except:
                pass

        db = KMeans(n_clusters=20, init="k-means++").fit_predict(np.array(timeSeries))



        for i,sensor in enumerate(sensor_list_with_P1):
            sensor.clusterNumber = db[i]
            sensor.save()

        for sensor in sensor_list_with_no_cluster:
            sensor.clusterNumber = -1
            sensor.save()




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


if __name__ == "__main__":
    test = ReadFromLuftdateInfoJSON()
    thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))