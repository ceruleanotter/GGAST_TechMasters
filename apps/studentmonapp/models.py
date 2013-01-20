from django.db import models
from swingtime.models import Occurrence, OccurrenceManager, Event
from profiles.models import Profile 
from dateutil import rrule
from django.core.urlresolvers import reverse
from datetime import datetime
from django.conf import settings
from django.forms.models import inlineformset_factory
from django.db import models
# Create your models here.
class MonitorReport(Occurrence):
    """
    """
    FUTUREEVENT = 'FE'
    ONTIME  = 'OK'
    COVERED = 'CO'
    LATE = 'LT'
    MISSED = 'MS'

    STATUS_CHOICES = (
        ('FE', 'Future duty'),
        ('OK', 'Signed in on time'),
        ('CO', 'Covered by another person'),
        ('LT', 'Signed in late'),
        ('MS', 'Monitor missed hours')
        )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,default=STATUS_CHOICES[0][0])
    signed_time = models.DateTimeField('Date Signed In',null=True, blank=True, default=None)
    user = models.ForeignKey(Profile, null=True, blank=True, default=None,related_name='reports')
    cover_reason = models.TextField(max_length=250)
    #getting the manager from the superclass
    objects = OccurrenceManager()


    def get_responsible_monitor(self):
        return self.event_type.profile

    def is_on_time_now (self, currenttime):

        print "IS ON TIME: called with %s" % (currenttime)
        
        late_enough = (currenttime > (self.end_time - settings.STUDENTM_SIGNIN_BEFORE_DELTA))
        print "IS ON TIME: late enough: %s" % (late_enough)
        
        on_time =  ((currenttime < (self.end_time + settings.STUDENTM_SIGNIN_AFTER_DELTA)) and late_enough)
        
        print "IS ON TIME: on_time: %s" % (on_time)
        
        return on_time, late_enough

    def is_not_attempting_cover(self, profile):
        return (self.get_responsible_monitor() == profile)

    def can_report(self, profile, currenttime):
        #three cases
        #the person is the right person and they are signing in on time
        #the person is right but signing in late
        #the time is right and another person is covering
        #first going to check the time
        print "CAN REPORT: called"
        if not(self.status == self.FUTUREEVENT or self.status == self.MISSED):
            print "CAN_REPORT: not a future event or missed"
            return False
        timeOK, lateEnough = self.is_on_time_now(currenttime)
        
        personOK = self.is_not_attempting_cover(profile)
        
        return (timeOK or (personOK and lateEnough))

    def get_issue_form(self,post_data=None):
        
        IssueFormSet = inlineformset_factory(MonitorReport,MonitorIssue,
                                             fields=('severity','description','attempted_troubleshooting','solved'),
                                             extra=4,
                                             can_delete=False)
        if post_data:
            return IssueFormSet(post_data,instance=self)
        return IssueFormSet(instance=self)
        

    

    def __unicode__(self):
        mon = self.get_responsible_monitor()
        coverstring = mon.name
        if (self.status ==  self.COVERED):
            coverstring = "%s covered for %s" % (self.user.name, mon.name)

        return "%s, STATUS: %s, MONITOR %s," % (self.start_time.date(), self.status, coverstring)


    #@models.permalink
    def get_absolute_url(self):
        return reverse('monitor_report_detail_view', args = [self.id])

class MonitorIssue(models.Model):
    EMERGENCY = 1
    HIGHP  = 2
    DISTRUPTIVE = 3
    WANT = 4

    SEVERITY_CHOICES = (
        (EMERGENCY, 'Emergency - Needs to be fix immediatly for safety or function of lab.'),
        (HIGHP, 'High Priority - Needs to be fixed soon for the lab to be working at full capacity.'),
        (DISTRUPTIVE, 'Distruptive - Would be good to fix soon; an annoyance.'),
        (WANT, 'Want - Something that isnt keeping students from learning or something that is a suggested feature.'),
        )
    NOTSOLVED = 0
    SOLVED = 1
    NA = 2

    SOLVED_CHOICES = (
        (NOTSOLVED, 'Not Solved'),
        (SOLVED, 'SOLVED!'),
        (NA, 'No longer applicable'),
        )
    monitor_report = models.ForeignKey(MonitorReport, blank=True, null=True, default=None, related_name='issues')
    severity = models.PositiveSmallIntegerField(max_length=1, choices=SEVERITY_CHOICES,default=SEVERITY_CHOICES[1][0])
    time_discovered = models.DateTimeField('Date issue discovered')
    date_solved = models.DateTimeField('Date issue solved', blank=True, null=True, default=None)
    user = models.ForeignKey(Profile)
    description = models.TextField(max_length=500)
    attempted_troubleshooting = models.TextField(max_length=500)
    solved = models.SmallIntegerField(max_length=1, choices=SOLVED_CHOICES,default=SOLVED_CHOICES[0][0]) 
    def __unicode__(self):
        """
        """
        return "%s, SOLVED? %s" % (self.description, self.solved)
    def get_absolute_url(self):
        return reverse('monitor_issue_detail_view', args=[self.id])
    #@models.permalink
    #def get_absolute_url(self):
    #    return('monitor_event_detail',[str(self.id)])

# proxy class for event type to override add event
class MonitorEvent(Event):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('monitor_event_detail_view', args=[self.id])
    def reports(self):
        occu = self.occurrence_set.all()
        reports = []
        for o in occu:
            try:
                report = o.monitorreport
                reports.append(report)
            except MonitorReport.DoesNotExist:
                print "Not a monitor report"
        return reports

    def add_occurrences(self, start_time, end_time, **rrule_params):
        #COPIED FROM SWINGTIME MODELS, EVENT, but occurence_Set.create changed to more explicit making of monitor reports.
           '''
        Add one or more occurences to the event using a comparable API to 
        ``dateutil.rrule``. 
        
        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.
        
        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.
        
        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        '''
           print "MonitorEvent: add_occurences called"
           rrule_params.setdefault('freq', rrule.DAILY)
           
           if 'count' not in rrule_params and 'until' not in rrule_params:
                mr = MonitorReport(start_time=start_time, end_time=end_time)
                mr.save(force_insert=True)
           else:
                delta = end_time - start_time
                for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                    mr = MonitorReport(event=self,start_time=ev, end_time=ev + delta)
                    mr.save(force_insert=True)
