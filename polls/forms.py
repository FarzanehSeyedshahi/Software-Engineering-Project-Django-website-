import datetime
from datetime import timezone

from django.contrib.auth.models import User
from django.contrib.auth import (authenticate, get_user_model)
from django import forms
from .models import Event
from .models import EventOption

User = get_user_model()

# class UserForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = ['username', 'password']

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self,*args,**kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username,password=password)
            if not user :
                raise forms.ValidationError('this User is not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Password is wrong')
            if not user.is_active:
                raise forms.ValidationError('this User is not Active')
            return super(UserLoginForm, self).clean( *args, **kwargs)

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email Adress: ')
    email2 = forms.EmailField(label='Confirm Email: ')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','email','email2','password']
##############################################
    def clean(self,*args,**kwargs):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email != email2:
             raise forms.ValidationError("emails must match")
        email_qs = User.objects.filter(email= email)
        if email_qs.exists():
            raise forms.ValidationError("This email was used before")
        return super(UserRegisterForm,self).clean(*args,**kwargs)
##############################################



class CreateEventForm(forms.ModelForm):
    ending_date = forms.DateField(label='Ending date', widget=forms.SelectDateWidget, initial=datetime.date.today)

    class Meta:
        model = Event
        fields = ('name', 'description', 'repeating_day', 'ending_date')


class SignUpForm(forms.ModelForm):
    # birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class EventOptionForm(forms.ModelForm):
    from_date = forms.DateField(label='from date', widget=forms.SelectDateWidget, initial=datetime.date.today)
    to_date = forms.DateField(label='to date', widget=forms.SelectDateWidget, initial=datetime.date.today)
    from_time = forms.TimeField(label='from time', widget=forms.TimeInput(format='%H:%M'))
    to_time = forms.TimeField(label='to time', widget=forms.TimeInput(format='%H:%M'))

    class Meta:
        model = EventOption
        fields = ('description', 'from_date', 'from_time', 'to_date', 'to_time')


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
