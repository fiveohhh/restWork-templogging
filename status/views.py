# Create your views here.
from django.http import HttpResponse
from restInterface.models import Temp_entry, door_entry, hvac_runtime
from django.template import Context, loader
import datetime
from django.core.cache import cache

def getHistoryToGraph(querySetOfTemp_entry):
    historyCnt = range(290)#we want the last 72*4 entries
    retArray = []
    for i in historyCnt:
        if i % 4 == 0:
            temp =  str(((querySetOfTemp_entry[i].temp/100.0) - 273.15) * 1.8 + 32) 
            retArray.append(temp)
    retArray.reverse() 
    return retArray #oldest first

def GetInHMS(seconds):
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    return "[%02d,%02d,%02d]" % (hours, minutes, seconds)

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
        
        #TODO Format these strings so they look decent on the web page
        tempEntry['temp'] = str(((t.temp/100.0) - 273.15) * 1.8 + 32) + 'F' 
        tempEntry['updated'] = str(datetime.datetime.fromtimestamp(t.dateTime))
        tempEntry['name'] = ''
        if t.sensor == 48:
            tempEntry['name'] += 'Garage: '
        elif t.sensor == 49:
            tempEntry['name'] += 'Outside: '
        elif t.sensor == 50:
            tempEntry['name'] += 'Kitchen: ' 
        else:
            tempEntry['name'] += 'Unknown: '
        temps.append(tempEntry)
   
    ############# END Get temps ###############


 
    ######### Get history to graph###############
    # out of the last 24 hours(24*(12 readings an hour=288entris))
    # take every 4th point (72 total) for the sensors you want
    # on the main status page, this stuff will all be hardcoded since
    # since we only want specific vals to display
    #########
    # get outside temps, newest entries first
    revOutsideTempHistory = Temp_entry.objects.filter(sensor=49).order_by('dateTime').reverse()
    cache.set('temp_entries', revOutsideTempHistory,120)
    cache.get('temp_entries') 
    outsideTemps = getHistoryToGraph(revOutsideTempHistory)

    revInsideTempHistory = Temp_entry.objects.filter(sensor=50).order_by('dateTime').reverse()
    cache.set('temp_entriesi', revInsideTempHistory,120)
    cache.get('temp_entriesi') 
    kitchenTemps = getHistoryToGraph(revInsideTempHistory)
    print str(len(kitchenTemps))
    plotPointList = []
    historyCnt = range(72)
    for i in historyCnt:
        plotPoint = {} 
        plotPoint['kitchen'] = kitchenTemps[i]
        plotPoint['outside'] = outsideTemps[i]
        plotPoint['hms'] = GetInHMS(i*20*60)#20 minutes, 60 seconds in a minute
        plotPointList.append(plotPoint)
   
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
        'plotPointList' : plotPointList,
    })

    return HttpResponse(t.render(c))

