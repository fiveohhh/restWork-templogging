# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from restInterface.models import Temp_entry, door_entry, hvac_runtime, Presence_entry
from django.template import Context, loader
import datetime
from django.core.cache import cache
import time
from ConfigParser import SafeConfigParser
from settings import SETTINGS_FILE

#returns the string for numbered sensor
def getSensorName(sensor):
    parser = SafeConfigParser()
    parser.read(SETTINGS_FILE)
    for t_sensor in parser.options('temp sensors'):
        if sensor == int(t_sensor):
            return parser.get('temp sensors',t_sensor)
    return 'Unknown'

# Holds information from a single temp logging event
class IndividualTempReading:
    def __init__(self, dateTime, temp):
        self.dateTime = dateTime
        self.temp = temp

# Will return 'numberOfDataPoints' that are evenly divided for the past 'secondsWorthOfHistory
# queryset should be filtered for an individual sensor if desired output is only for a single sensor
def getHistoryWithDateTime(queryset, secondsWorthOfHistory, numberOfDataPoints):
    # Get a time object that is secondsWorthOfHistory in length
    delta = datetime.timedelta(seconds = secondsWorthOfHistory)

    # Get current time  
    now = datetime.datetime.now()

    # Get a dateTimeObject that represents the earliest time we want to get data from
    dateTimeOfOldestEntry = now - delta

    # Convert dateTime to a unix timestamp
    unixTimeOfOldestEntry = time.mktime(dateTimeOfOldestEntry.timetuple())
    
    # Filter queryset to only items within our desired history
    timeFilteredSet = queryset.filter(dateTime__gte=unixTimeOfOldestEntry)

    # Order oldest to newest
    revTimeFilteredSet = timeFilteredSet.order_by('dateTime').reverse()

    # Get number of items in queryset
    numOfEntries = revTimeFilteredSet.count()

    # If there is no history, return an empty list
    if numOfEntries == 0:
        emptyList = []
        return emptyList
    
    
    modVal = 0
    
    # Need a separate dataPOints in case we ask for more than is available.
    # if that is the case, we will return everything we have
    dataPoints = 0
    if numberOfDataPoints >= numOfEntries:
        # If we ask for more than we have, return everything we have
        modVal = 1
        dataPoints = numOfEntries
    else:
        # else we want to grab dataPoints worth of data that is evenly
        # spaced throughout our history
        modVal = (numOfEntries/numberOfDataPoints) + 1
        dataPoints = numberOfDataPoints
    
    dataRange = range(numOfEntries)
    retList = []
    i = 0
    print time.time()
    for t in revTimeFilteredSet:
        i = i+1
        if i % modVal == 0:
            ent = t
            tempF = (((ent.temp/100.0) - 273.15) * 1.8 + 32) 
            retList.append(IndividualTempReading(datetime.datetime.fromtimestamp(ent.dateTime),tempF))
    retList.reverse()
    print time.time()
    return retList 


# Renders a page for a detailed request for an individual sensor
def detailedTemp(request, sensor):
    sensorName = getSensorName(sensor)
    revTempHistory = Temp_entry.objects.filter(sensor=sensor)
    temps = getHistoryWithDateTime(revTempHistory, 3600*24*7*4*12, 200)
    latestReading = {}
    print 'sensor: '
    print sensor
    latestReading['name'] = getSensorName(int(sensor))
    t = loader.get_template('status/detailedTemp.html')
    c = Context({
        'temps' : temps,
        'latestReading' : latestReading
    })

    return HttpResponse(t.render(c))


    #get years worth of data

    #divide into resonable amount of data points for one year graph

    #divide into amounts for 6 month 

    #divide into amounts for 1 month

    #divide into amounts for 1 week

    #divide into amounts for 1 day


# renders main summary page for status
@login_required
def index(request):
    # Get presence vals to display on status page
    presences = []
    parser = SafeConfigParser()
    parser.read(SETTINGS_FILE)
    if parser.has_option('presence', 'displayed_status'):
        opts = parser.get('presence', 'displayed_status')
        opts = opts.split(',')
        opts = [o.strip() for o in opts]
        for o in opts:
            if parser.has_option('presence', o):
                presence = {}
                presenceHistory = Presence_entry.objects.filter(presence_ID = o)
                lastEntry = presenceHistory.order_by('dateTime').reverse()[0]
                presence['name'] = parser.get('presence', o)
                presence['dateTime'] = str(datetime.datetime.fromtimestamp(lastEntry.dateTime))
                presence['location'] = parser.get('location',str(lastEntry.location))
                presence['arrived_or_left'] = 'left'
                if lastEntry.isArriving:
                    presence['arrived_or_left'] = 'arrived at'
                presences.append(presence)

 



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
        tempEntry['temp'] = str(round(((t.temp/100.0) - 273.15) * 1.8 + 32,1)) + 'F' 
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
    outsideTempHistory = getHistoryWithDateTime(Temp_entry.objects.filter(sensor=49), 60*60*24, 6*24)# last 24 hours of data, 6 readings an hour
    cache.set('temp_entries_o', outsideTempHistory,120)
    cache.get('temp_entries_o') 

    insideTempHistory = getHistoryWithDateTime(Temp_entry.objects.filter(sensor=50), 60*60*24, 6*24)
    cache.set('temp_entries_i', insideTempHistory,120)
    cache.get('temp_entries_i')
    
    garageTempHistory = getHistoryWithDateTime(Temp_entry.objects.filter(sensor=48), 60*60*24, 6*24)
    cache.set('temp_entries_g', garageTempHistory,120)
    cache.get('temp_entries_g')
    


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
    
    parser = SafeConfigParser()
    parser.read(SETTINGS_FILE)


    for d in lastDoorVals:
        door = {}
        door['name'] = 'Unknown: '
    
        if parser.has_option('doors', str(d.doorNumber)):
            door['name'] = parser.get('doors', str(d.doorNumber))
        
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
        'presences' : presences,
        'hvac_usage' : hvac_usage,
        'outsideTempHistory' : outsideTempHistory,
        'insideTempHistory' : insideTempHistory,
        'garageTempHistory' : garageTempHistory
    })

    return HttpResponse(t.render(c))

