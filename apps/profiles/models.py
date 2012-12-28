from django.db import models
from django.utils.translation import ugettext_lazy as _

from idios.models import ProfileBase

from swingtime.models import EventType

class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True, blank=True)
    website = models.URLField(_("website"), null=True, blank=True, verify_exists=False)
    event_type = models.OneToOneField(EventType)
    def __unicode__(self):
        return "Name: %s -- %s" % (self.name, self.about)


