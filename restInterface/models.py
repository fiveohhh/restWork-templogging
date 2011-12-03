from django.db import models

class Temp_entry(models.Model):
    dateTime = models.IntegerField() #datetime as unixepoch gmt
    sensor = models.IntegerField()   # id of sensor
    temp = models.IntegerField()     # temp as temp in Kelvin * 100
