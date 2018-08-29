from django.urls import path, register_converter
from django.conf.urls import url

from . import views, converters

register_converter(converters.FourDigitYearConverter, 'intList')

urlpatterns = [
    path('', views.detailHome, name='Home'),
    # ex: /polls/5/
    path('<int:owner_id>/', views.detailHome, name='detailHome'),
    path('map', views.detailHexMap, name='Map'),
    path('about', views.detailAbout, name='About'),
    # ex: /polls/5/results/
    path('<int:sensor_id>/value/', views.value, name='value'),
    #path('api/<int:sensor_ids>/getSensorData', views.linechart_chartjs, name='get_linechart_chartjs'),
    path('api/<str:value_type>/<intList:sensor_ids>/getSensorData', views.linechart_chartjs, name='get_linechart_chartjs'),
    path('api/<str:value_type>/getSensorData', views.getHexbinData2, name='getHexbinData'),
    path('api/<str:value_type>/<str:longitude>/<str:latitude>/getClosestSensorData', views.getClosestSensorData, name='getClosestSensorData'),
    path('loaderio-e6cf2c0cf1b08e7744911746b57b6f5d/',views.getloaderio,name='getloaderio')

]

