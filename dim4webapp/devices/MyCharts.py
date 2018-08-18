from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import Sensor, Owner, SensorValue
import random
import time
from django.utils import timezone
from datetime import timedelta

class TimeLineChartView(BaseLineChartView):
    def get_context_data(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        context.update({'datasets': self.get_datasets()})
        return context
    def get_datasets(self):
        datasets = []
        color_generator = self.get_colors()
        data = self.get_data()
        providers = self.get_providers()
        num = len(providers)
        for i, entry in enumerate(data):
            color = tuple(next(color_generator))
            dataset = {'backgroundColor': "rgba(%d, %d, %d, 0.5)" % color,
                       'borderColor': "rgba(%d, %d, %d, 1)" % color,
                       'pointBackgroundColor': "rgba(%d, %d, %d, 1)" % color,
                       'pointBorderColor': "#fff",
                       'fill': False,
                        'pointRadius': 0,
                       'lineTension': 0,
                       'data': entry}
            if i < num:
                dataset['label'] = providers[i]  # series labels for Chart.js
                dataset['name'] = providers[i]  # HighCharts may need this
            datasets.append(dataset)
        return datasets

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
    value_type = 'P1'
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
            values = list(SensorValue.objects.filter(sensor=id,type=self.kwargs['value_type'],created__range=[timezone.now()-timedelta(days=3),timezone.now()]).order_by('created').values('created', 'value'))
            timeData = [time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(d['created'].timetuple()))) for d in values]
            ydata = [float(d['value']) for d in values]
            dictList = []
            for i in range(len(timeData)):
                dict =  {}
                dict["x"] = timeData[i]
                dict["y"] = ydata[i]
                dictList.append(dict)
            listDictList.append(dictList)

        return random.sample(listDictList,min(len(listDictList),10))


class TimeChartClusterJSONView(TimeLineChartView):
    cluster_id = 0
    value_type = 'P1'
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]


    def get_providers(self):
        """Return names of datasets."""
        return [str(d.id) for d in Sensor.objects.filter(clusterNumber=self.kwargs['cluster_id'])]

    def get_data(self):
        """Return 3 datasets to plot."""
        listDictList = []
        sensor_list = Sensor.objects.filter(clusterNumber=self.kwargs['cluster_id'])
        for sensor in sensor_list:
            values = list(SensorValue.objects.filter(sensor=sensor.id,type=self.value_type).order_by('created').values('created', 'value'))
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
