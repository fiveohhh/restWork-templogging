from django.http import HttpResponse

def insert(request, sensor, temp, datetime):
    return HttpResponse("tempis %s" % sensor)


