from django.apps import AppConfig
from django_cron import CronJobBase, Schedule
from .models import Sensor, Owner, SensorValue
import json
import urllib.request
from django.contrib.gis.geos import Point
import asyncio
import websockets as ws


async def test():
    async with ws.connect(
            r'wss://eu1.loriot.io/app?token=vnoTPgAAAA1ldTEubG9yaW90LmlvioIq8UeQhDkDJ-VVtrbZNQ==') as websocket:
        await websocket.send('hello')
        response = await websocket.recv()
        data = json.loads(response)

        print(data)

asyncio.get_event_loop().run_until_complete(test())