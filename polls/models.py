#todo: i changed model.
from builtins import bool

from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import datetime
from django.contrib.auth.models import User


class User(models.Model):
    email = models.EmailField(primary_key = True)
    # event = models.ForeignKey(Event, on_delete=models.CASCADE)
    # time_of_authorization = models.DateTimeField(default=now)
    # event_items = models.ManyToManyField(EventOption)

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    repeating_day = models.IntegerField(default=0)
    active_status = models.BooleanField(default=1)
    holding_date_to = models.DateTimeField()
    holding_date_from = models.DateTimeField()
    ending_date = models.DateTimeField(blank=True)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    creating_date = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    def was_published_recently(self):
        return self.pub_date >= now - datetime.timedelta(days=1)

    def is_active(self):
        return bool(self.active_status)


class EventOption(models.Model):
    yes_count = models.IntegerField(default=0)
    no_count = models.IntegerField(default=0)
    maybe_count = models.IntegerField(default=0)
    has_chosen = models.BooleanField(default=0)
    description = models.TextField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "id")

    def __str__(self):
        return self.description


class ParticipateIn(models.Model):
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "participant", "id")


class Comment(models.Model):
    date = models.DateTimeField(default=now)
    text = models.TextField()
    event_option = models.ForeignKey(EventOption, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event_option", "commenter", "id")


class ReplyComment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    new_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='new_comment')
    replied_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='old_comment')

    class Meta:
        unique_together = ("new_comment", "commenter", "replied_comment", "id")

# class Event(models.Model):
#     event_name = models.CharField(max_length=200)
#     email_of_creator = models.EmailField()
#     description = models.TextField()
#     # id = models.CharField(max_length=50, primary_key=True)
#
#     def __str__(self):
#         return self.event_name
#
#     def was_published_recently(self):
#         return self.pub_date >= now - datetime.timedelta(days=1)
#
#
# class EventOption(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     event_item_name = models.CharField(max_length=100)
#     event_date=models.DateField('day')
#     event_date_from_time=models.DateTimeField('From')
#     event_date_to_time = models.DateTimeField('To')
#     content = models.DateTimeField()
#     votes = models.IntegerField(default=0)
#     #votes_sofar = models.IntegerField(votes)
#
#     def __str__(self):
#         return self.event_item_name
#
# class Participant(models.Model):
#     name = models.CharField(max_length=100)
#     event = models.ForeignKey(Event,  on_delete=models.CASCADE)
#     time_of_authorization = models.DateTimeField(default=now)
#     event_items = models.ManyToManyField(EventOption)

# Create your models here.