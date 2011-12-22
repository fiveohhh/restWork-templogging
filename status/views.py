# Create your views here.
from django.http import HttpResponse
from restInterface.models import Temp_entry
from django.template import Context, loader
import datetime

def index(request):
    lastTemps = Temp_entry.objects.order_by('dateTime').reverse()[:2]
    thisWork = str(lastTemps)

    temps = []    

    for t in lastTemps:
        name = 'Unknown: '
        if t.sensor == 48:
            name = 'Garage: '
        elif t.sensor == 49:
            name = 'Outside: '
        
        temp = str(((t.temp/100) - 273.15) * 1.8 + 32) + 'F   Last Updated:'
        updated = str(datetime.datetime.fromtimestamp(t.dateTime))
        out = name + temp + updated
        temps.append( "".join(out))
    
    t = loader.get_template('status/index.html')
    c = Context({
        'temps' : temps,
    })

    return HttpResponse(t.render(c))

