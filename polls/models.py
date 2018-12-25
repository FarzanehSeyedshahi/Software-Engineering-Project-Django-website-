from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import datetime


class Event(models.Model):
    event_name = models.CharField(max_length=200)
    email_of_creator = models.EmailField()
    description = models.TextField()
    # id = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.event_name

    def was_published_recently(self):
        return self.pub_date >= now - datetime.timedelta(days=1)


class EventOption(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_item_name = models.CharField(max_length=100)
    event_date=models.DateField('day')
    event_date_from_time=models.DateTimeField('From')
    event_date_to_time = models.DateTimeField('To')
    content = models.DateTimeField()
    votes = models.IntegerField(default=0)
    #votes_sofar = models.IntegerField(votes)

    def __str__(self):
        return self.event_item_name


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    time_of_authorization = models.DateTimeField(default=now)
    event_items = models.ManyToManyField(EventOption)


class Participant(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event,  on_delete=models.CASCADE)
    time_of_authorization = models.DateTimeField(default=now)
    event_items = models.ManyToManyField(EventOption)

# Create your models here.
