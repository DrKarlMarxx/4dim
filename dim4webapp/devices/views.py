from django.shortcuts import render
from django.http import HttpResponse
from .models import Sensor, Owner, SensorValue, CurrentSensorValue
from django.template import loader
from django.template.loader import render_to_string
from django.http import JsonResponse
from chartit import DataPool, Chart
from django.shortcuts import render_to_response
from django_ajax.decorators import ajax
from django.core.serializers import serialize
import datetime
import time
import json
from chartjs.views.lines import BaseLineChartView
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

import json
import urllib.request


from .MyCharts import LineChartJSONView, TimeChartJSONView, TimeChartClusterJSONView


def index(request):
    latest_owner_list = Owner.objects.order_by('id')[:5]
    template = loader.get_template('devices/index.html')
    context = {'latest_owner_list': latest_owner_list}

    return HttpResponse(template.render(context, request))
# Create your views here.

def detail(request, owner_id):
    owner_sensor_list = Sensor.objects.filter(owner=owner_id)

    template = loader.get_template('devices/detail.html')
    context = {'owner_sensor_list': owner_sensor_list}

    return HttpResponse(template.render(context,request))


def detailHex(request):

    value_type_list = SensorValue.objects.order_by().values_list('type', flat=True).distinct()
    cluster_list = Sensor.objects.order_by('clusterNumber').values_list('clusterNumber', flat=True).distinct()
    value_type_list = [d for d in value_type_list]
    value_type_list.insert(0, value_type_list.pop(value_type_list.index('P1')))

    template = loader.get_template('devices/detailBootstrap.html')
    context = {'value_type_list': value_type_list,'cluster_list':cluster_list}

    return HttpResponse(template.render(context,request))


def getHexbinData(request, value_type):
    result = dict()
    sensor_list = []
    owner_id=1
    owner_sensor_list = Sensor.objects.filter(owner=owner_id)
    for sensorInstance in owner_sensor_list:
        try:
            values = dict()
            sensorInstance.currentvalue = float(CurrentSensorValue.objects.filter(sensor=sensorInstance.id, type=value_type)[0].value)
            values['longitude']=sensorInstance.longitude
            values['latitude']=sensorInstance.latitude
            values['id']=sensorInstance.id
            values['currentvalue']=sensorInstance.currentvalue
            sensor_list.append(values)
        except:
            pass
    result['data'] = sensor_list
    return JsonResponse(result, safe=False)


def getHexbinData2(request, value_type):
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
    try:
        closestSensor = Sensor.objects.filter(id__in=sensor_id_list).annotate(distance=Distance('geom', base_point)).order_by('distance').first()
        result['distance'] = int(closestSensor.distance.m)
        result['data'] = CurrentSensorValue.objects.filter(sensor_id = closestSensor.id)[0].value
    except:
        result['distance'] = 'not found'
        result['data'] = 'not found'
    geoNamesRequestUrl = r'http://api.geonames.org/findNearbyJSON?lat=' + str(latitude) + '&lng=' + str(
        longitude) + '&username=DrKarlMarxx'
    try:
        with urllib.request.urlopen(geoNamesRequestUrl) as urlJson:
            geoNamesData = json.loads(urlJson.read())
        result['name'] = geoNamesData["geonames"][0]["toponymName"]
    except:
        result['name'] = 'unknown'

    return JsonResponse(result, safe=False)


def get_linechart(request,sensor_id):
    """
    lineChart page
    """
    value_list = list(SensorValue.objects.filter(sensor=sensor_id).order_by('created').values('created', 'value'))

    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 150
    xdata = [time.mktime(d['created'].timetuple())*1000 for d in value_list]

    ydata = [float(d['value']) for d in value_list]


    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie1 = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
    }

    chartdata = {'x': xdata,
        'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie1, 'kwargs1': { 'color': '#a4c639' },
    }

    charttype = "lineChart"
    chartcontainer = 'linechart_container'  # container name
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    output_file = open('test_lineChart.html', 'w')
    output_file.write(render_to_string('devices/linechart.html', data))
    output_file.close()
    return render_to_response('devices/linechart.html', data)

@ajax
def get_linechart_base(request, sensor_id):
    """
    lineChart page
    """
    value_list = list(SensorValue.objects.filter(sensor=sensor_id).order_by('created').values('created', 'value'))

    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 150
    xdata = [time.mktime(d['created'].timetuple()) * 1000 for d in value_list]

    ydata = [float(d['value']) for d in value_list]

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
    }
    kwargs1 = {'color': 'black'}
    type = "lineChart"
    chart = lineChart(name=type, x_is_date=False, x_axis_format="AM_PM")
    chart.add_serie(y=ydata, x=xdata, name='sine', extra=extra_serie, **kwargs1)
    output_file = open('test_lineChart.html', 'w')
    chart.buildcontent()
    output_file.write(chart.htmlcontent)
    output_file.close()
    return chart.htmlcontent


@ajax
def get_linechart_list(request, sensor_ids):
    """
    lineChart page
    """
    value_list = list(SensorValue.objects.filter(sensor=sensor_ids[0]).order_by('created').values('created', 'value'))

    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 150
    xdata = [time.mktime(d['created'].timetuple()) * 1000 for d in value_list]

    ydata = [float(d['value']) for d in value_list]

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " cal"},
        "date_format": tooltip_date,
    }
    kwargs1 = {'color': 'black'}
    type = "lineChart"
    chart = lineChart(name=type, x_is_date=False, x_axis_format="AM_PM")
    chart.add_serie(y=ydata, x=xdata, name='sine', extra=extra_serie, **kwargs1)
    output_file = open('test_lineChart.html', 'w')
    chart.buildcontent()
    output_file.write(chart.htmlcontent)
    output_file.close()
    return chart.htmlcontent


@ajax
def get_linechart_chartjs(request, sensor_ids):
    """
    lineChart page
    """
    #value_list = list(SensorValue.objects.filter(sensor=sensor_ids[0]).order_by('created').values('created', 'value'))

    #start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    #nb_element = 150
    #xdata = [time.mktime(d['created'].timetuple()) * 1000 for d in value_list]

    #ydata = [float(d['value']) for d in value_list]
    bla = LineChartJSONView()
    line_chart_json = LineChartJSONView.as_view()
    return line_chart_json


linechart_chartjs = TimeChartJSONView.as_view(sensor_ids=0,value_type=['P1'])
linechart_chartjs_cluster = TimeChartClusterJSONView.as_view(cluster_id=0,value_type='P1')

@ajax
def getSensorData(request, sensor_id):
    data = SensorValue.objects.filter(sensor=sensor_id).values('created','value')
    return JsonResponse(list(data), safe=False)

def value(request, sensor_id):
    value_list = SensorValue.objects.filter(sensor=sensor_id).values('created','value')
    template = loader.get_template('devices/showValues.html')
    context = {'value_list': value_list}
    return HttpResponse(template.render(context,request))

def getloaderio(request):
    content = 'loaderio-e6cf2c0cf1b08e7744911746b57b6f5d'
    return HttpResponse(content, content_type='text/plain')

