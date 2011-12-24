# Create your views here.
from django.http import HttpResponse
from restInterface.models import Temp_entry
from django.template import Context, loader
import datetime

def index(request):
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
        name = 'Unknown: '
        if t.sensor == 48:
            name = 'Garage: '
        elif t.sensor == 49:
            name = 'Outside: '
        elif t.sensor == 50:
            name = 'Kitchen: ' 
        
        #TODO Format these strings so they look decent on the web page
        temp = str(((t.temp/100) - 273.15) * 1.8 + 32) + 'F   Last Updated:'
        updated = str(datetime.datetime.fromtimestamp(t.dateTime))
        out = name + temp + updated
        temps.append( "".join(out))
    
    t = loader.get_template('status/index.html')
    c = Context({
        'temps' : temps,
    })

    return HttpResponse(t.render(c))

