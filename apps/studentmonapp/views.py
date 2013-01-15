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
from django.conf import settings
from django.db.models import Q

def userhome(request):
    #need some checks to redirect if not the right user
    #page_user = get_object_or_404(User, username=username)
    #if (request.user != page_user): return HttpResponse("Access Denied")
    page_user = request.user
    #things are fine, keep going
    profile = get_object_or_404(Profile, user=page_user)
    reported_issues = profile.monitorissue_set.all()
    
    upcoming_reports = MonitorReport.objects.daily_occurrences(dt=None) # grabs today only
    upcoming_reports = upcoming_reports.filter(status__exact=MonitorReport.FUTUREEVENT) # gets rid of reports already signed in to
    currenttime = datetime.now()
    okstart_endtime = currenttime - settings.STUDENTM_SIGNIN_AFTER_DELTA
    okend_endtime = currenttime + settings.STUDENTM_SIGNIN_BEFORE_DELTA
    
    # upcoming_reports = upcoming_reports.filter(Q(end_time__range=(okstarttime,okendtime)) | Q(event__event_type__exact=profile.event_type))
    missed_reports_today = upcoming_reports.filter(end_time__lt=okstart_endtime).filter(event__event_type__exact=profile.event_type)
    upcoming_reports = upcoming_reports.filter(end_time__range=(okstart_endtime,okend_endtime))
    


    late_reports = MonitorReport.objects.filter(status__exact=MonitorReport.MISSED)
    late_reports = late_reports.filter(event__event_type__exact=profile.event_type)
    
    return render_to_response('studentmonapp/userhome.html',
                              {'profile' : profile,
                               'upcoming_reports' : upcoming_reports,
                               'missed_reports_today' : missed_reports_today,
                               'late_reports' : late_reports,
                               'reported_issues' : reported_issues,
                               },
                              context_instance=RequestContext(request))  


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

    inlineIssues = report.get_issue_form() # probably need to move this in the if; make sure to show the exsisting instances

    if request.method == 'POST' and can_report: # If the form has been submitted..
        form = CheckInForm(request.POST, nocover=is_correct_person, instance=report,prefix='checkin') # A form bound to the POST data, updating report
        
        inlineIssues = report.get_issue_form(post_data=request.POST)
        
        print "Monitor Report Detail: post attempted, can cover is %s and form valid is %s and errors are %s" % (can_report, form.is_valid(), form.errors )
        
        #!!! there might be issues with the whole prefix thing, look for using more than one formset
        if (form.is_valid() or not(len(form.errors))) and (inlineIssues.is_valid()): # All validation rules pass and the time is still ok, so not valid because no new data, but we just needed to see the post
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

            #saving the formset of issues
            issues_to_save = inlineIssues.save(commit=False)
            for issue in issues_to_save:
                issue.monitor_report = report
                issue.time_discovered = currenttime
                issue.user = userprofile
                issue.save()
            
            return HttpResponseRedirect(reverse('monitor_report_detail_view',args=(report_id,))) # Redirect after POST
    else:
        form = None

        if (can_report):
            form = CheckInForm(instance=report, nocover=is_correct_person,prefix='checkin')

    return render_to_response('studentmonapp/monitor_report_detail.html',
                              {'occurrence' : report,
                               'form':form,
                               'inlineform':inlineIssues,
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
