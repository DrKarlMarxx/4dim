from django.urls import path, register_converter
from django.conf.urls import url

from . import views, converters

register_converter(converters.FourDigitYearConverter, 'intList')

urlpatterns = [
    path('', views.detailHome, name='Home'),
    path('map', views.detailHexMap, name='Map'),
    path('about', views.detailAbout, name='About'),
    path('api/<str:value_type>/<intList:sensor_ids>/getSensorData', views.linechart_chartjs, name='get_linechart_chartjs'),
    path('api/<str:value_type>/getSensorData', views.getHexbinData, name='getHexbinData'),
    path('api/<str:value_type>/<str:longitude>/<str:latitude>/getClosestSensorData', views.getClosestSensorData, name='getClosestSensorData'),
    path('loaderio-e6cf2c0cf1b08e7744911746b57b6f5d/',views.getloaderio,name='getloaderio')

]

