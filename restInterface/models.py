from django.db import models
import datetime

class Temp_entry(models.Model):
    dateTime = models.IntegerField() #datetime as unixepoch gmt
    sensor = models.IntegerField()   # id of sensor
    temp = models.IntegerField()     # temp as temp in Kelvin * 100
    def __unicode__(self):
        return ('GMT: ' + str(datetime.datetime.fromtimestamp(self.dateTime)) + '\n' +
                'Sensor: ' + str(self.sensor) + '\n' +
                'Temp(K): ' + str(self.temp/100) + '\n')
