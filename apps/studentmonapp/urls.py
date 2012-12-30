from django.conf.urls.defaults import *
from django.views.generic import DetailView
from studentmonapp.models import MonitorEvent

urlpatterns = patterns('studentmonapp.views',
                        (r'^admin/createuserschedule/$','createuserschedule'),
                        (r'^user/(?P<username>[\w\._-]+)/$','userhome'),
                       url(r'^report/(?P<report_id>\d+)/$', 'monitor_report_detail', name='monitor_report'),
                       url(r'^monitorhours/(?P<pk>\d+)/$',
                        DetailView.as_view( model=MonitorEvent,
                                            template_name='studentmonapp/monitor_event_detail.html',
                                            context_object_name='event',
                                            ),
                           name='monitor_event_detail',
                        ),
                       )
