from django.http import HttpResponse
from restInterface.models import Temp_entry, door_entry
from django.db.models import Max
import time
import datetime

MINIMUM_SECONDS_BETWEEN_TEMP_LOGGING = 60 * 9


def insert(request, s, t, d):
    # override incoming time with current server time github issue#2
    currentTime = round(time.time())
    lastEntryForSensor = Temp_entry.objects.filter(sensor=s).aggregate(Max('dateTime'))
    lastTimeEntryOccured = lastEntryForSensor['dateTime__max']
   
    retString = ''
 
    secondsSinceLastEntry = currentTime - lastTimeEntryOccured
    if secondsSinceLastEntry >= MINIMUM_SECONDS_BETWEEN_TEMP_LOGGING:  
        te = Temp_entry.create(int(currentTime), int(s), int(t))
        te.save()
        retString += '{Succesful:Logged:' + t + ' to sensor:' + s + '}'
    else:
        retString += '{Msg:Not Logged, last entry was ' + str(secondsSinceLastEntry) + ' seconds ago}' 
    return HttpResponse(retString)

def processMsg(request, msg):
    if (msg.startswith("DOR")):
        # DORXYZ -- X=destination, Y=doorNumber, Z=isOpen
        # Door status message received
        doorNumber = int(msg[4])
        isOpen = int(msg[5])
        dateTime = time.time()
        doorEntry = door_entry.create(dateTime, doorNumber, isOpen)
        doorEntry.save()
        print doorEntry
    else:
        print "Unknown detected"
        # Unknown message received
    
    return HttpResponse("ok")
