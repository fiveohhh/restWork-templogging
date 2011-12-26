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

class door_status:
    doorNumber = models.IntegerField()  # Door that reported a status change
    isOpen = models.IntegerField()      # 0=closed 1=open
    dateTime = models.IntegerField()    # datetime as unixepoch gmt

    def create(date, doorNum, isOpe):
        print isOpe
        return door_status(dateTime = date, doorNumber = doorNum, isOpen = isOpe)
    create = staticmethod(create)

    def __unicode__(self):
        return ('GMT: ' + str(datetime.datetime.fromtimestamp(self.dateTime)) + '\n' +
                'Door#: ' + str(doorNumber) + '\n' +
                'isOpen: ' + str(isOpen) + '\n')
                 
