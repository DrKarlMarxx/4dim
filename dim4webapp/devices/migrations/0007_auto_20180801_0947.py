# Generated by Django 2.0.7 on 2018-08-01 09:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_auto_20180801_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensorvalue',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 1, 9, 47, 45, 42994, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='sensorvalue',
            name='type',
            field=models.CharField(max_length=100),
        ),
    ]