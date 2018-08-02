from django.shortcuts import render
from django.http import HttpResponse
from .models import Sensor, Owner, SensorValue
from django.template import loader
from django.template.loader import render_to_string
from django.http import JsonResponse
from chartit import DataPool, Chart
from django.shortcuts import render_to_response
from django_ajax.decorators import ajax
from django.core.serializers import serialize
import datetime
import time
from nvd3 import lineChart
from chartjs.views.lines import BaseLineChartView


from .MyCharts import LineChartJSONView, TimeChartJSONView


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


def detailHex(request, owner_id):
    owner_sensor_json = serialize('geojson',Sensor.objects.filter(owner=owner_id), geometry_field='point',fields=('location',))
    owner_sensor_list = Sensor.objects.filter(owner=owner_id)
    sensor_list = []
    for sensorInstance in owner_sensor_list:
        try:
            sensorInstance.currentvalue = float(SensorValue.objects.filter(sensor=sensorInstance.id,type='P1').last().value)
            sensor_list.append(sensorInstance)
        except:
            pass
    template = loader.get_template('devices/detailHex.html')
    context = {'owner_sensor_list': sensor_list}

    return HttpResponse(template.render(context,request))


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


linechart_chartjs = TimeChartJSONView.as_view(sensor_ids=0)

@ajax
def getSensorData(request, sensor_id):
    data = SensorValue.objects.filter(sensor=sensor_id).values('created','value')
    return JsonResponse(list(data), safe=False)

def value(request, sensor_id):
    value_list = SensorValue.objects.filter(sensor=sensor_id).values('created','value')
    template = loader.get_template('devices/showValues.html')
    context = {'value_list': value_list}
    return HttpResponse(template.render(context,request))

