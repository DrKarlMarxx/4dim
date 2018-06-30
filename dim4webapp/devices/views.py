from django.shortcuts import render
from django.http import HttpResponse
from .models import Sensor, Owner, SensorValue
from django.template import loader
from django.http import JsonResponse


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

def getSensorData(request, sensor_id):
    data = SensorValue.objects.filter(sensor=sensor_id).values('created','value')
    return JsonResponse(list(data), safe=False)

def value(request, sensor_id):
    response = "You're looking at the values of question %s."
    return HttpResponse(response % sensor_id)

