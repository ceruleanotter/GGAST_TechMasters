from django.conf.urls.defaults import *
from django.views.generic import DetailView
from studentmonapp.models import MonitorEvent, MonitorIssue

urlpatterns = patterns('studentmonapp.views',
                        (r'^admin/createuserschedule/$','createuserschedule'),
                       url(r'^user/$','userhome',name="userhome"),
                       url(r'^report/(?P<report_id>\d+)/$', 'monitor_report_detail', name='monitor_report_detail_view'),
                       url(r'^monitorhours/(?P<pk>\d+)/$',
                        DetailView.as_view( model=MonitorEvent,
                                            template_name='studentmonapp/monitor_event_detail.html',
                                            context_object_name='event',
                                            ),
                           name='monitor_event_detail_view',
                        ),
                       url(r'^monitorissue/(?P<pk>\d+)/$',
                           'monitor_issue_view',
                           name='monitor_issue_detail_view',
                        ),
                       )

''' DetailView.as_view( model=MonitorIssue,
                                            template_name='studentmonapp/monitor_issue_detail.html',
                                            context_object_name='issue',
                                            ),'''
