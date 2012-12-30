from swingtime.forms import MultipleOccurrenceForm
from studentmonapp.models import MonitorEvent, MonitorReport
from django.forms import ModelForm

class CheckInForm(ModelForm):
    """
    """
    class Meta:
        model = MonitorReport
        exclude = ('status','signed_time','user','start_time','end_time','event','notes',)
    def __init__(self,*args,**kwargs):
        """
        """
        nocover = kwargs.pop('nocover',None)
        super(CheckInForm,self).__init__(*args, **kwargs)
        if nocover:
            del self.fields['cover_reason']

class MultipleReportFormException(Exception):
    pass


class MultipleReportForm(MultipleOccurrenceForm):
    """
    """
    ###copied from multipleoccurenceform
    def save(self, event):
        print "MultipleReportForm: save called"
        if self.cleaned_data['repeats'] == 'no':
            params = {}
        else:
            params = self._build_rrule_params()
        if isinstance(event, MonitorEvent):
            print "MultipleReportForm: is and instance of Monitor event, saving"
            event.add_occurrences(
                self.cleaned_data['start_time'], 
                self.cleaned_data['end_time'],
                **params
                )
        else :
            raise MultipleReportFormException("You are trying to save an event that is not a MonitorEvent using save in the MultipleReportForm")
        return event
    
class ReportEventForm(ModelForm):

    class Meta:
        model = MonitorEvent
        
    #---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(ReportEventForm, self).__init__(*args, **kws)
        self.fields['description'].required = False
