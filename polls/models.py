from __future__ import unicode_literals
from builtins import bool
from django.utils.translation import gettext
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
# from schedule.models import Event, EventRelation, Calendar
from django.core.mail import EmailMessage



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
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,null=True)
    day = models.DateField(u'Day of the event', help_text=u'Day of the event')
    start_time = models.TimeField(u'Starting time', help_text=u'Starting time')
    end_time = models.TimeField(u'Final time', help_text=u'Final time')
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = u'Scheduling'
        verbose_name_plural = u'Scheduling'

    def create_busyDate(self,event_option_name):
        busy_date = self.create( notes = event_option_name)
        return busy_date

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:    #edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (new_end >= fixed_start and new_end <= fixed_end): #innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end: #outter limits
            overlap = True

        return overlap

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a href="%s">%s</a>' % (url, str(self.start_time))

    def send_email_for_overlap(self,participate_emails):
        subject = "Confilict Event!"
        email_body = " your new event : have overlap with other events!\n we set it but be careful.\n goodluck:)"
        email = EmailMessage(subject, email_body, 'asis.meetingscheduler@gmail.com', participate_emails)
        email.send()
        return

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('Ending hour must be after the starting hour')

        events = BusyDate.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                if self.check_overlap(event.start_time, event.end_time, self.start_time, self.end_time):
                    raise ValidationError(
                        'There is an overlap with another event: ' + str(event.day) + ', ' + str(
                            event.start_time) + '-' + str(event.end_time))

