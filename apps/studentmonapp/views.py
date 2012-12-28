# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from idios.utils import get_profile_model
from profiles.models import Profile
from django.contrib.auth.models import User
from studentmonapp.models import MonitorIssue, MonitorReport
from swingtime.models import OccurrenceManager
from django.http import HttpResponse
def userhome(request, username):
    #need some checks to redirect if not the right user
    page_user = get_object_or_404(User, username=username)
    if (request.user != page_user): return HttpResponse("Access Denied")
    
    #things are fine, keep going
    profile = get_object_or_404(Profile, user=page_user)
    reportedIssues = MonitorIssue.objects.filter(user__exact=page_user)
    upcoming_reports = OccurrenceManager.daily_occurences()
    upcoming_reports = upcoming_reports.filter(status__exact='FE')
    late_reports = MonitorReport.objects.filter(status__exact='LT')
    


    return HttpResponse("profile object is, I swear %s " % profile
)
