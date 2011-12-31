# Create your views here.
from django.http import HttpResponse
from restInterface.models import Temp_entry, door_entry, hvac_runtime
from django.template import Context, loader
import datetime
from django.core.cache import cache
import time

# for status page only
def getHistoryToGraph(querySetOfTemp_entry):
    historyCnt = range(290)#we want the last 72*4 entries
    retArray = []
    for i in historyCnt:
        if i % 4 == 0:
            temp =  str(((querySetOfTemp_entry[i].temp/100.0) - 273.15) * 1.8 + 32) 
            retArray.append(temp)
    retArray.reverse() 
    return retArray #oldest first

# convert seconds to HMS
def GetInHMS(seconds):
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    return "[%02d,%02d,%02d]" % (hours, minutes, seconds)

#returns the string for numbered sensor
def getSensorName(sensor):
    if sensor == 48: 
        return 'Garage'
    elif sensor == 49:
        return 'Outside'
    elif sensor == 50:
        return 'Kitchen'
    else:
        return 'Unknown'

class IndividualTempReading:
    def __init__(self, dateTime, temp):
        self.dateTime = dateTime
        self.temp = temp

# queryset should be ordered and have newest entry first
def getHistoryWithDateTime(queryset, secondsWorthOfHistory, numberOfDataPoints):
    delta = datetime.timedelta(seconds = secondsWorthOfHistory) 
    now = datetime.datetime.now()
    dateTimeOfOldestEntry = now - delta
    unixTimeOfOldestEntry = time.mktime(dateTimeOfOldestEntry.timetuple())
    timeFilteredSet = queryset.filter(dateTime__gte=unixTimeOfOldestEntry)
    numOfEntries = timeFilteredSet.count()
    if numOfEntries == 0:
        emptyList = []
        return emptyList
    
    modVal = 0
    dataPoints = 0
    if numberOfDataPoints >= numOfEntries:
        modVal = 1
        dataPoints = numOfEntries
    else:
        modVal = (numOfEntries/numberOfDataPoints) + 1
        dataPoints = numberOfDataPoints
    print modVal
    print ' ' + str(dataPoints)
    dataRange = range(numOfEntries)
    retList = []
    print time.time()
    for i in dataRange:
        if i % modVal == 0:
            ent = timeFilteredSet[i]
            tempF = (((ent.temp/100.0) - 273.15) * 1.8 + 32) 
            retList.append(IndividualTempReading(datetime.datetime.fromtimestamp(ent.dateTime),tempF))
    retList.reverse()
    print time.time()
    return retList 


def detailedTemp(request, sensor):
    sensorName = getSensorName(sensor)
    revTempHistory = Temp_entry.objects.filter(sensor=sensor).order_by('dateTime').reverse()
    temps = getHistoryWithDateTime(revTempHistory, 3600*24*7*4*12, 200)
    t = loader.get_template('status/detailedTemp.html')
    c = Context({
        'temps' : temps,
    })

    return HttpResponse(t.render(c))


    #get years worth of data

    #divide into resonable amount of data points for one year graph

    #divide into amounts for 6 month 

    #divide into amounts for 1 month

    #divide into amounts for 1 week

    #divide into amounts for 1 day


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
        tempEntry['name'] = getSensorName(t.sensor) + ': '
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

