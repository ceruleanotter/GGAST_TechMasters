from django.db import models
from django.utils.translation import ugettext_lazy as _


#for signals
from django.db.models.signals import post_save
from django.dispatch import receiver

from idios.models import ProfileBase

from swingtime.models import EventType

class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    event_type = models.OneToOneField(EventType, null=True)
    def __unicode__(self):
        return "Name: %s -- %s" % (self.name, self.about)
    def get_username(self):
        return self.user.username
        


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
