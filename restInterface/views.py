from django.http import HttpResponse
from restInterface.models import Temp_entry, door_entry
import time

def insert(request, s, t, d):
    # override incoming time with current server time github issue#2
    currentTime = round(time.time())
    te = Temp_entry.create(int(currentTime), int(s), int(t))
    te.save()
    retString = s + ' temp:' + t + ' date:' + d
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
