from django.db import models
import datetime

class Temp_entry(models.Model):
    dateTime = models.IntegerField() #datetime as unixepoch gmt
    sensor = models.IntegerField()   # id of sensor
    temp = models.IntegerField()     # temp as temp in Kelvin * 100
    
    def create(date, sen, tmpVal):
        print tmpVal
        return Temp_entry(dateTime = date, sensor = sen, temp = tmpVal)
    create = staticmethod(create) 

    def __unicode__(self):
        return ('GMT: ' + str(datetime.datetime.fromtimestamp(self.dateTime)) + '\n' +
                'Sensor: ' + str(self.sensor) + '\n' +
                'Temp: ' + str(self.temp) + '\n')
