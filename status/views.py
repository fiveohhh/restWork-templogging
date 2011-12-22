# Create your views here.
from django.http import HttpResponse
from restInterface.models import Temp_entry

def index(request):
    lastTemps = Temp_entry.objects.order_by('dateTime').reverse()[:2]
    thisWork = str(lastTemps)
    return HttpResponse(lastTemps)

