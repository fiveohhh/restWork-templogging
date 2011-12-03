from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^restInterface/$', 'restInterface.views.index'),
    url(r'^restInterface/sensor=(?P<sensor>\d+),temp=(?P<temp>\d+),datetime=(?P<datetime>\d+)/$','restInterface.views.insert'),


    # Examples:
    # url(r'^$', 'leeHouseSite.views.home', name='home'),
    # url(r'^leeHouseSite/', include('leeHouseSite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
