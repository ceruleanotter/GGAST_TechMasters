from django.conf.urls.defaults import *

urlpatterns = patterns('studentmonapp.views',
                       (r'^(?P<username>[\w\._-]+)/$','userhome'),
                       )
