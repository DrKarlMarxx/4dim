from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView, TimeLineChartView
from .models import Sensor, Owner, SensorValue
import random
import time

class LineChartJSONView(BaseLineChartView):
    sensor_id = 0
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]


class TimeChartJSONView(TimeLineChartView):
    sensor_ids = 0
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]


    def get_providers(self):
        """Return names of datasets."""
        return [str(d) for d in self.kwargs['sensor_ids']]

    def get_data(self):
        """Return 3 datasets to plot."""
        listDictList = []
        for id in self.kwargs['sensor_ids']:
            values = list(SensorValue.objects.filter(sensor=id,type='P1').order_by('created').values('created', 'value'))
            timeData = [time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(d['created'].timetuple()))) for d in values]
            ydata = [float(d['value']) for d in values]
            dictList = []
            for i in range(len(timeData)):
                dict =  {}
                dict["x"] = timeData[i]
                dict["y"] = ydata[i]
                dictList.append(dict)
            listDictList.append(dictList)

        return random.sample(listDictList,min(len(listDictList),20))
