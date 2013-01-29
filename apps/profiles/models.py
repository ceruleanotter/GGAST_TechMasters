from django.db import models
from django.utils.translation import ugettext_lazy as _
from studentmonapp.models import MonitorReport
from django.db.models import Q, Count

#for signals
from django.db.models.signals import post_save
from django.dispatch import receiver


from idios.models import ProfileBase

from swingtime.models import EventType

class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    event_type = models.OneToOneField(EventType, null=True, editable=False)
    score = models.FloatField(editable=False, default=0)
    def __unicode__(self):
        return "%s" % (self.name)
    def get_username(self):
        return self.user.username
    def calc_score(self):
        all_duties = MonitorReport.objects.filter(Q(user__exact=self)| Q(event__event_type__exact=self.event_type)).exclude(status__exact=MonitorReport.FUTUREEVENT)
        ontime = all_duties.filter(user__exact=self).filter(Q(status__exact=MonitorReport.COVERED) | Q(status__exact=MonitorReport.ONTIME))
        ontime_len = len(ontime)
        score = ontime_len - (len(all_duties.filter(status__exact=MonitorReport.LATE))*2) -  (len(all_duties.filter(status__exact=MonitorReport.MISSED))*3)+0.5*len(ontime.annotate(num_issues=Count('issues')).filter(num_issues__gt=0))
        self.score = score
        self.save()

    def get_stats(self):
        all_duties = MonitorReport.objects.filter(Q(user__exact=self)| Q(event__event_type__exact=self.event_type)).exclude(status__exact=MonitorReport.FUTUREEVENT)
        ontime = all_duties.filter(user__exact=self).filter(Q(status__exact=MonitorReport.COVERED) | Q(status__exact=MonitorReport.ONTIME))
        perOnTime = -1
        perLate = -1
        if len(all_duties) == 0:
            perOnTime ="N/A"
            perLate ="N/A"
        else:
            ontime_len = len(ontime)  
            perOnTime = ontime_len*100/len(all_duties)
            late_len = len(all_duties.filter(Q(status__exact=MonitorReport.LATE) | Q(status__exact=MonitorReport.MISSED)))
            perLate =  late_len*100/len(all_duties)
        
        return {'OnTime':perOnTime,'Late':perLate,'Score':self.score}


def create_User_EventType(sender, instance, created, **kwargs):
    print "checking creation of profile"
    if created:
        print "User event type is being created"
        name = instance.get_username()
        event_label = "%s_hours" % (name)
        print "the event label is" + event_label
        et = EventType.objects.create(abbr=name,label=event_label)
        et.save()
        instance.event_type = et;
        instance.save()

post_save.connect(create_User_EventType,sender=Profile,dispatch_uid="event_post_save_for_profile")
