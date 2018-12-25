from django.contrib.auth.models import User
from django import forms
from .models import Event
from .models import EventOption


class UserForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','password']
from django import forms


class CreateEventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields=('event_name','email_of_creator','description',)


class SignUpForm(forms.ModelForm):
    #birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')

    class Meta:
        model = User
        fields = ('first_name', 'last_name','username', 'email','password' )

class EventOptionForm(forms.ModelForm):
    event_date = forms.DateField(label='event_date', widget=forms.SelectDateWidget)
    event_date_from_time = forms.DateField(label='event_date_from_time', widget=forms.SelectDateWidget)
    event_date_to_time = forms.DateField(label='event_date_to_time', widget=forms.SelectDateWidget)
    content = forms.DateField(label='content', widget=forms.SelectDateWidget)
    class Meta:
        model = EventOption
        fields = ('event_item_name', 'event_date', 'event_date_from_time', 'event_date_to_time', 'content',
        'votes')

class EventForm(forms.ModelForm):
    class Meta:
        model = EventOption
        fields = ('event','event_item_name', 'event_date', 'event_date_from_time', 'event_date_to_time', 'content','votes' ,)