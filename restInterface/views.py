from django.http import HttpResponse
from restInterface.models import Temp_entry

def insert(request, s, t, d):
    te = Temp_entry.create(int(d), int(s), int(t))
    te.save()
    retString = s + ' temp:' + t + ' date:' + d
    return HttpResponse(retString)


