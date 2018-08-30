from django.http import HttpResponse
from .models import Sensor, Owner, SensorValue, CurrentSensorValue
from django.template import loader
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
import json
import urllib.request
from .MyCharts import TimeChartJSONView


def detailHexMap(request):

    value_type_list = SensorValue.objects.order_by().values_list('type', flat=True).distinct()
    cluster_list = Sensor.objects.order_by('clusterNumber').values_list('clusterNumber', flat=True).distinct()
    value_type_list = [d for d in value_type_list]
    value_type_list.insert(0, value_type_list.pop(value_type_list.index('P1')))

    template = loader.get_template('devices/detailBootstrapMap.html')
    context = {'value_type_list': value_type_list,'cluster_list':cluster_list}

    return HttpResponse(template.render(context,request))


def detailHome(request):

    template = loader.get_template('devices/detailBootstrapHome.html')
    value_type_list = SensorValue.objects.order_by().values_list('type', flat=True).distinct()
    value_type_list = [d for d in value_type_list]
    value_type_list.insert(0, value_type_list.pop(value_type_list.index('P1')))
    context = {'value_type_list': ['P1']}

    return HttpResponse(template.render(context,request))

def detailAbout(request):

    template = loader.get_template('devices/about.html')

    context = {}

    return HttpResponse(template.render(context,request))




def getHexbinData(request, value_type):
    result = dict()
    sensor_list = []
    owner_id=1
    sensor_data_list = CurrentSensorValue.objects.filter(type=value_type)
    for sensorValueInstance in sensor_data_list:
        try:
            values = dict()
            values['currentvalue'] = float(sensorValueInstance.value)
            sensorInstance = Sensor.objects.filter(id=sensorValueInstance.sensor_id)[0]
            values['longitude']=sensorInstance.longitude
            values['latitude']=sensorInstance.latitude
            values['id']=sensorInstance.id
            sensor_list.append(values)
        except:
            pass
    result['data'] = sensor_list
    return JsonResponse(result, safe=False)


def getClosestSensorData(request, value_type,longitude,latitude):
    result = dict()
    longitude = float(longitude)
    latitude = float(latitude)
    sensor_id_dict = CurrentSensorValue.objects.filter(type=value_type).values('sensor_id')
    sensor_id_list = [d['sensor_id'] for d in sensor_id_dict]
    base_point = Point(longitude,latitude,srid =4326)
    result['owner']=''
    try:
        closestSensor = Sensor.objects.filter(id__in=sensor_id_list).annotate(distance=Distance('geom', base_point)).order_by('distance').first()
        result['owner'] = Owner.objects.filter(id=closestSensor.owner_id)[0].name
        result['distance'] = int(closestSensor.distance.m)
        result['data'] = CurrentSensorValue.objects.filter(sensor_id = closestSensor.id)[0].value
        result['longitude'] = closestSensor.longitude
        result['latitude'] = closestSensor.latitude
        result['id']=closestSensor.id
    except:
        result['distance'] = 'not found'
        result['data'] = 'not found'
        result['id']=False
        result['longitude'] = False
        result['latitude'] = False
    geoNamesRequestUrl = r'http://api.geonames.org/findNearbyJSON?lat=' + str(latitude) + '&lng=' + str(
        longitude) + '&username=DrKarlMarxx'
    try:
        with urllib.request.urlopen(geoNamesRequestUrl) as urlJson:
            geoNamesData = json.loads(urlJson.read())
        result['name'] = geoNamesData["geonames"][0]["toponymName"]
    except:
        result['name'] = 'unknown'

    return JsonResponse(result, safe=False)



linechart_chartjs = TimeChartJSONView.as_view(sensor_ids=0,value_type=['P1'])


def getloaderio(request):
    content = 'loaderio-e6cf2c0cf1b08e7744911746b57b6f5d'
    return HttpResponse(content, content_type='text/plain')

