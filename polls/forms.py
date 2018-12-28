from django.contrib.auth.models import User
from django import forms
from .models import Event
from .models import EventOption


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'description', 'repeating_day')


class SignUpForm(forms.ModelForm):
    # birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class CreateEventOptionForm(forms.ModelForm):
    date = forms.DateField(label='date', widget=forms.SelectDateWidget)

    class Meta:
        model = EventOption
        fields = ('description', 'date')


class ShowEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'description', 'repeating_day', 'ending_date', 'creator', 'creating_date',)


class ShowEventOptionFrom(forms.ModelForm):
    description = forms.Textarea()
    date = forms.DateTimeField(label='date', widget=forms.DateTimeField)
    yes_count = forms.IntegerField(label='yes', widget=forms.IntegerField)

    class Meta:
        model = EventOption
        fields = ('description', 'date', 'yes_count',)