from django.urls import path, register_converter
from django.conf.urls import url

from . import views, converters

register_converter(converters.FourDigitYearConverter, 'intList')

urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:owner_id>/', views.detailHex, name='detailHex'),
    path('<int:owner_id>/test', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:sensor_id>/value/', views.value, name='value'),
    #path('api/<int:sensor_ids>/getSensorData', views.linechart_chartjs, name='get_linechart_chartjs'),
    path('api/<intList:sensor_ids>/getSensorData', views.linechart_chartjs, name='get_linechart_chartjs'),
    ]

