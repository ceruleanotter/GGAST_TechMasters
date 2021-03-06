from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.views.generic import ListView
from profiles.models import Profile
from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer


handler500 = "pinax.views.server_error"

'''url(r"^$", ListView.as_view(
                queryset=Profile.objects.all(),
                context_object_name='profiles',
                template_name='homepage.html'),
        name="home"),'''

urlpatterns = patterns("",
    url(r"^$",'studentmonapp.views.home',name="home"),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^studentmonitors/",include("studentmonapp.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
