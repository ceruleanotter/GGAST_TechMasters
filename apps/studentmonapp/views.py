# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from idios.utils import get_profile_model
from profiles.models import Profile
from django.contrib.auth.models import User
from studentmonapp.models import MonitorIssue, MonitorReport
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from studentmonapp.forms import MultipleReportForm, ReportEventForm, CheckInForm
from swingtime.views import add_event
from datetime import datetime

def userhome(request, username):
    #need some checks to redirect if not the right user
    page_user = get_object_or_404(User, username=username)
    if (request.user != page_user): return HttpResponse("Access Denied")
    
    #things are fine, keep going
    profile = get_object_or_404(Profile, user=page_user)
    reportedIssues = MonitorIssue.objects.filter(user__exact=page_user)
    upcoming_reports = MonitorReport.objects.daily_occurrences(dt=None)
    upcoming_reports = upcoming_reports.filter(status__exact='FE')
    late_reports = MonitorReport.objects.filter(status__exact='LT')
    


    return HttpResponse("profile object is, I swear %s " % profile)


def monitor_report_detail(request, report_id):
    report = get_object_or_404(MonitorReport, pk=report_id)
    userprofile = request.user.get_profile()
    is_correct_person = report.is_not_attempting_cover(userprofile)
    currenttime = datetime.now()
    time_ok, late_enough = report.is_on_time_now(currenttime)
    print "Monitor Report Detail: The user is %s" % (userprofile)
    print "Monitor Report Detail: is_correct_person is %s" % (is_correct_person)
    can_report = report.can_report(userprofile, currenttime)
    if request.method == 'POST' and can_report: # If the form has been submitted...

        form = CheckInForm(request.POST, nocover=is_correct_person, instance=report) # A form bound to the POST data, updating report
        print "Monitor Report Detail: post attempted, can cover is %s and form valid is %s and errors are %s" % (can_report, form.is_valid(), form.errors )
        if (form.is_valid() or not(len(form.errors))): # All validation rules pass and the time is still ok, so not valid because no new data, but we just needed to see the post
            print "Monitor Report Detail: no errors and saving" % (userprofile) 
#check what the report status should be
            if not(is_correct_person):
                report.status = report.COVERED
            elif time_ok:
                report.status = report.ONTIME
            else:
                report.status = report.LATE

            report.signed_time = currenttime
            report.user = userprofile
            report.save()
            form.save()
            return HttpResponseRedirect(reverse('monitor_report',args=(report_id,))) # Redirect after POST
    else:
        form = None
        if (can_report):
            form = CheckInForm(instance=report, nocover=is_correct_person) 
    return render_to_response('studentmonapp/monitor_report_detail.html',
                              {'occurrence' : report,
                               'form':form,
                               'can_report_data':(can_report,is_correct_person,time_ok,late_enough),
                               'current_time':currenttime,
                               'user':request.user},
                              context_instance=RequestContext(request))  

def createuserschedule(request):
    print ("create user schedule called")
    if (not request.user.is_staff): return HttpResponse("Access Denied")
    return add_event(request, template='studentmonapp/createuserschedule.html', event_form_class=ReportEventForm, recurrence_form_class=MultipleReportForm)

'''    if request.method == 'POST': # If the form has been submitted...
        form = MultipleOccurrenceForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect(reverse('studentmonapp.views.userhome',args=(request.user.username))) # Redirect after POST
    else:
        form =  MultipleOccurrenceForm()# An unbound form

        return render_to_response('studentmonapp/createuserschedule.html', {'form': form, }, context_instance=RequestContext(request))
'''
