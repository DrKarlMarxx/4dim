
import json
import urllib.request

url = r'http://api.luftdaten.info/static/v2/data.json'
with urllib.request.urlopen(url) as urlJson:
    data = json.loads(urlJson.read())

for sensorData in data:


    name =str(sensorData['id'])
    idNumber=str(sensorData['id'])
    value=0.0
    latitude=float(sensorData['location']['latitude'])
    longitude=float(sensorData['location']['longitude'])
    location='None'
