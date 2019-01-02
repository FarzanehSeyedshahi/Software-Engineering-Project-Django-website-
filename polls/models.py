from builtins import bool

from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import datetime
from django.contrib.auth.models import User


# class User(models.Model):
#     email = models.EmailField(primary_key = True)
# event = models.ForeignKey(Event, on_delete=models.CASCADE)
# time_of_authorization = models.DateTimeField(default=now)
# event_items = models.ManyToManyField(EventOption)

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    repeating_day = models.IntegerField(default=0)
    active_status = models.BooleanField(default=1)
    holding_date_to = models.DateField(null=True)
    holding_time_to = models.TimeField(null=True)
    holding_date_from = models.DateField(null=True)
    holding_time_from = models.TimeField(null=True)
    ending_date = models.DateField(null=True)

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
    from_date = models.DateField()
    from_time = models.TimeField()
    to_date = models.DateField()
    to_time = models.TimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "id")

    def __str__(self):
        return self.description


class ParticipateIn(models.Model):
    participant_email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "participant_email", "id")


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


class BusyDate(models.Model):
    event_name = models.CharField(max_length=200)
    event_from_date = models.DateField()
    event_from_time = models.TimeField()
    event_to_date = models.DateField()
    event_to_time = models.TimeField()

    class Meta:
        unique_together = ("event_from_date", "event_from_time", "event_to_date", "event_to_time", "id")

    def check_overlap(self, from_date, from_time, to_date, to_time):
        if (self.event_from_date < from_date < self.event_to_date) or (
                self.event_from_date < to_date < self.event_to_date):
            if (self.event_from_time < from_time < self.event_to_time) or (
                    self.event_from_time < to_time < self.event_to_time):
                return True
        else:
            return False
