from django.db import models
import datetime

class Presence_entry(models.Model):
    dateTime = models.IntegerField(db_index=True)#datetime presence observed
    location = models.IntegerField(db_index=True)# location of presence
    presence_ID = models.IntegerField(db_index=True)# id of "thing"
    isArriving = models.IntegerField()# did thing leave or arrive

    # 0 if leaving 1 if arriving 
    def create(date, p_id, loc, leave_or_arrive):
        return Presence_entry(  dateTime = date, 
                                presence_ID = p_id,
                                location = loc, 
                                isArriving = leave_or_arrive)
    create = staticmethod(create)

class Temp_entry(models.Model):
    dateTime = models.IntegerField(db_index=True) #datetime as unixepoch gmt
    sensor = models.IntegerField(db_index=True)   # id of sensor
    temp = models.IntegerField()     # temp as temp in Kelvin * 100
    
    def create(date, sen, tmpVal):
        return Temp_entry(dateTime = date, sensor = sen, temp = tmpVal)
    create = staticmethod(create) 

    def __unicode__(self):
        return ('GMT: ' + str(datetime.datetime.fromtimestamp(self.dateTime)) + '\n' +
                'Sensor: ' + str(self.sensor) + '\n' +
                'Temp: ' + str(self.temp) + '\n')

class door_entry(models.Model):
    doorNumber = models.IntegerField()  # Door that reported a status change
    isOpen = models.IntegerField()      # 0=closed 1=open
    dateTime = models.IntegerField()    # datetime as unixepoch gmt

    def create(date, doorNum, isOpe):
        return door_entry(dateTime = date, doorNumber = doorNum, isOpen = isOpe)
    create = staticmethod(create)

    def __unicode__(self):
        return ('GMT: ' + str(datetime.datetime.fromtimestamp(self.dateTime)) + '\n' +
                'Door#: ' + str(self.doorNumber) + '\n' +
                'isOpen: ' + str(self.isOpen) + '\n')


# dateTime is the datetime that the entry was made.  data is for the previous day
class hvac_runtime(models.Model):
    dateTime = models.IntegerField()    # date reading was taken
    heatMinutes = models.IntegerField() # minutes heat was running
    coolMinutes = models.IntegerField() # minutes cool was running

    def create(date, heatMins, coolMins):
        return hvac_runtime(dateTime = date, heatMinutes = heatMins, coolMinutes = coolMins)
    create = staticmethod(create)

    def __unicode__(self):
        return('Usage on: ' + str((datetime.datetime.fromtimestamp(self.dateTime) - datetime.timedelta(days=1)).strftime('%m-%d-%y')) + '\n' +
                'heat: ' + str(self.heatMinutes) + '\n' +
                'cool: ' + str(self.coolMinutes) + '\n')


