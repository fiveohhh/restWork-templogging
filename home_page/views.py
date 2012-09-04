# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context, loader
import time


# renders main summary page for status
@login_required
def index(request):
    t = loader.get_template('home_page/index.html')
    something = 0
    c = Context({'something': something,})

    return HttpResponse(t.render(c))

