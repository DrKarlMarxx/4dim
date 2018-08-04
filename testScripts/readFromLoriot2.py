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

        print(data['data'])
        dataString = data['data']
        pm10 = int(dataString[0:4],16)/100.
        pm25 = int(dataString[4:8], 16) / 100.
        latitude = (int(dataString[8:16], 16)-2147483648) / 1000000.
        longitude= (int(dataString[16:24], 16)-2147483648) / 1000000.
        print('pm = '+str(pm10))
        print('latitude = ' +str(latitude))
        print('longitude = '+str(longitude))

asyncio.get_event_loop().run_until_complete(test())

