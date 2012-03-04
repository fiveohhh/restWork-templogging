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
        processDoorMsg(msg) 
    else:
        print "Unknown detected"
        # Unknown message received
    
    return HttpResponse("ok")

def processDoorMsg(msg):
    # DORXYZ -- X=destination, Y=doorNumber, Z=isOpen
    # Door status message received
    msgIsOpen = int(msg[5])
    msgDoorNumber = int(msg[4])

    # we want to get the last reported status. If it is the same, no sense logging
    # it.  This will let us send repeat messages to the server in case one is 
    # missed.

    # If last message for this door is different than the current msg
    lastEntry = door_entry.objects.filter(doorNumber=msgDoorNumber).order_by('-pk')[0]
    if lastEntry.isOpen != msgIsOpen:
        dateTime = time.time()
        doorEntry = door_entry.create(dateTime, msgDoorNumber, msgIsOpen)
        doorEntry.save()
    

