from django.db import models
from swingtime.models import Occurrence
from profiles.models import Profile 
# Create your models here.
class MonitorReport(Occurrence):
    """
    """
    STATUS_CHOICES = (
        ('FE', 'Future Event'),
        ('OK', 'Signed in on time'),
        ('CO', 'Covered by another person'),
        ('LT', 'Signed in late'),
        ('MS', 'Monitor missed hours')
        )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,default=STATUS_CHOICES[0][0])
    signed_time = models.DateTimeField('Date Signed In',null=True)
    user = models.ForeignKey(Profile)
    cover_reason = models.TextField(max_length=250)
    
    def get_responsible_monitor(self):
        return self.event_type.profile
    def __unicode__(self):
        mon = self.get_responsible_monitor(self)
        coverstring = mon.name
        if (self.status == self.STATUS_CHOICES['CO']):
            coverstring = "%s covered for %s" % (self.user.name, mon.name)

        return "%s, STATUS: %s, MONITOR %s," % (self.start_time.date(), self.status, coverstring)

class MonitorIssue(models.Model):
    SEVERITY_CHOICES = (
        (1, 'Emergency: Needs to be fix immediatly for safety or function of lab.'),
        (2, 'High Priority: Needs to be fixed soon for the lab to be working at full capacity.'),
        (3, 'Distruptive: Would be good to fix soon; an annoyance.'),
        (4, 'Want: Something that isnt keeping students from learning or something that is a suggested feature.'),
        )
    SOLVED_CHOICES = (
        (0, 'Not Solved'),
        (1, 'SOLVED!'),
        (2, 'No longer applicable'),
        )
    monitor_report = models.ForeignKey(MonitorReport)
    severity = models.PositiveSmallIntegerField(max_length=1, choices=SEVERITY_CHOICES,default=SEVERITY_CHOICES[1][0])
    time_discovered = models.DateTimeField('Date issue discovered')
    date_solved = models.DateTimeField('Date issue solved')
    user = models.ForeignKey(Profile)
    description = models.TextField(max_length=500)
    attempted_troubleshooting = models.TextField(max_length=500)
    solved = models.SmallIntegerField(max_length=1, choices=SOLVED_CHOICES,default=SOLVED_CHOICES[0][0]) 
    def __unicode__(self):
        """
        """
        return "%s, SOLVED? %s" % (self.description, self.solved)
        
    
