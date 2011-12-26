# Create your views here.
from django.http import HttpResponse
from restInterface.models import Temp_entry, door_entry, hvac_runtime
from django.template import Context, loader
import datetime

def index(request):
   
    ############ Get temps ###############
    # Get distinct sensor values
    distinctSensorVals = Temp_entry.objects.values('sensor').distinct()
    
    lastTemps = []
    
    # Get last entry for each one of our distict sensor values
    for sensor in distinctSensorVals:
        sensorHistory = Temp_entry.objects.filter(sensor=sensor['sensor'])
        lastEntry = sensorHistory.order_by('dateTime').reverse()[0]
        lastTemps.append(lastEntry)
    
    temps = []    
    
    # Put into readable string
    for t in lastTemps:
        tempEntry = {}
        tempEntry['name'] = ''
        if t.sensor == 48:
            tempEntry['name'] += 'Garage: '
        elif t.sensor == 49:
            tempEntry['name'] += 'Outside: '
        elif t.sensor == 50:
            tempEntry['name'] += 'Kitchen: ' 
        else:
            tempEntry['name'] += 'Unknown: '
        #TODO Format these strings so they look decent on the web page
        tempEntry['temp'] = str(((t.temp/100.0) - 273.15) * 1.8 + 32) + 'F' 
        tempEntry['updated'] = str(datetime.datetime.fromtimestamp(t.dateTime))
        temps.append(tempEntry)
    ############# END Get temps ###############


    ############ Get doors ####################
    distinctDoorVals = door_entry.objects.values('doorNumber').distinct()
    
    # list of last door_entry objects
    lastDoorVals = []

    # List of display strings for door status
    doors = []

    for door in distinctDoorVals:
        doorHistory = door_entry.objects.filter(doorNumber=door['doorNumber'])
        lastEntry = doorHistory.order_by('dateTime').reverse()[0]
        lastDoorVals.append(lastEntry)

    for d in lastDoorVals:
        door = {}
        door['name'] = 'Unknown: '
        if d.doorNumber == 0:
            door['name'] = 'Garage: '
        
        door['doorStatus'] = "Open"
        if d.isOpen == 0:
            door['doorStatus'] = "Closed"

        door['updated'] = str(datetime.datetime.fromtimestamp(d.dateTime))
        
        doors.append(door)
    ############## END Get doors #####################
    
    ############## Get latest HVAC usage #############
    lastHvacEntry = hvac_runtime.objects.all().order_by('dateTime').reverse()[0]
    hvac_usage = []
    
    hvac_entry = {}
    hvac_entry['heatUsage'] =  str(lastHvacEntry.heatMinutes)
    hvac_entry['coolUsage'] =  str(lastHvacEntry.coolMinutes)

    hvac_usage.append(hvac_entry)
    ############ END Get latest HVAC usage ############

    t = loader.get_template('status/index.html')
    c = Context({
        'temps' : temps,
        'doors' : doors,
        'hvac_usage' : hvac_usage,
    })

    return HttpResponse(t.render(c))

