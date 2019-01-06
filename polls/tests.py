import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from django.test import Client
from polls.models import Event, EventOption
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.contrib.auth.models import User
from .models import Event, EventOption, Comment, ReplyComment, ParticipateIn, BusyDate
from .views import *



class EventModelTests(TestCase):

    def setUp(self):
        self.client = Client()


    def create_event(self, name, description, creator):
        event = Event.objects.create(name=name, description=description, creator=creator)
        return event


    def create_EventOptions(self, description, from_date, from_time, to_date, to_time, event):
        event_option = EventOption.objects.create(
            description=description, event=event,
            from_date=from_date, from_time=from_time,
            to_date=to_date, to_time=to_time
        )
        return event_option


    def create_user(self, username, email):
        user = User.objects.create(username=username, email=email)
        return user


    def create_participate_in(self, email, event):
        participate_in = ParticipateIn.objects.create(participant_email=email, event=event)
        return participate_in


    def create_busy_date(self, user, day, start_time, end_time, name):
        busy_date = BusyDate.objects.create(
            user=user, day=day, start_time=start_time, end_time=end_time, name=name
        )
        return busy_date


    def test_has_overlap(self):
        user = self.create_user("test username", "test@test.com")
        creator = self.create_user("test creator username", "testcreator@test.com")
        event = self.create_event("test event", "test description", creator)
        self.create_participate_in("test@test.com", event)
        self.create_busy_date(user, "2019-1-13", "11:10", "11:20", "test event")
        self.create_EventOptions("first test event option", "2019-1-13", "11:15", "2019-1-13", "11:30", event)
        event_options = EventOption.objects.all()
        self.assertTrue(has_overlap(1, event_options, 0, user))
        self.assertFalse(has_overlap(2, event_options, 0, user))
        self.assertFalse(has_overlap(2, event_options, 0, user))


    def test_vote_with_one_choice(self):
        user = self.create_user("test", "test@test.com")
        creator = self.create_user("test creator username", "testcreator@test.com")
        event = self.create_event("test event", "test description", creator)
        event_option1 = self.create_EventOptions("first test event option", "2019-1-13", "11:45", "2019-1-13",
                                                 "12:00", event)
        event_option2 = self.create_EventOptions("second test event option", "2019-1-13", "12:30", "2019-1-13",
                                                 "13:00", event)
        self.client.force_login(user)
        response = self.client.post('/1/vote/', {"eventoption1": 1})
        self.assertEqual(response.status_code, 302, "test_vote, status code")


    def test_vote_with_without_any_choice(self):
        user = self.create_user("test", "test@test.com")
        creator = self.create_user("test creator username", "testcreator@test.com")
        event = self.create_event("test event", "test description", creator)
        event_option1 = self.create_EventOptions("first test event option", "2019-1-13", "11:45", "2019-1-13",
                                                 "12:00", event)
        event_option2 = self.create_EventOptions("second test event option", "2019-1-13", "12:30", "2019-1-13",
                                                 "13:00", event)
        self.client.force_login(user)
        response = self.client.post('/1/vote/')
        self.assertEqual(response.status_code, 200, "test_vote, status code")
        self.assertContains(response, "You didn&#39;t select a choice.")


    @mock.patch.object(EmailMessage, "__init__", return_value=None)
    @mock.patch.object(EmailMessage, "send")
    def test_save_participate(self, mock_send, mock_init):
        user = self.create_user("test", "test@test.com")
        creator = self.create_user("test creator username", "testcreator@test.com")
        event = self.create_event("test event", "test description", creator)
        event_option1 = self.create_EventOptions("first test event option", "2019-1-13", "11:45", "2019-1-13",
                                                 "12:00", event)
        event_option2 = self.create_EventOptions("second test event option", "2019-1-13", "12:30", "2019-1-13",
                                                 "13:00", event)

        response = self.client.post('/1/saveparticipate/', {'participate_number1': 'test@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Schedule your <b>meetings</b> and <b>events</b> with pleasure!")
        mock_init.assert_called_with(event.name, mock.ANY, 'asis.meetingscheduler@gmail.com', mock.ANY)


    def test_complete_scenario_of_vote(self):
        user = self.create_user("test username", "test@test.com")
        creator = self.create_user("test creator username", "testcreator@test.com")
        event = self.create_event("test event", "test description", creator)
        event_option1 = self.create_EventOptions("first test event option", "2019-1-13", "11:45", "2019-1-13",
                                                 "12:00", event)
        event_option2 = self.create_EventOptions("second test event option", "2019-1-13", "12:30", "2019-1-13",
                                                 "13:00", event)
        self.client.force_login(user)
        self.client.post('/event/')
        self.client.post('/1/')
        response = self.client.post('/1/vote/', {"eventoption1": 2})

        self.assertEqual(response.status_code, 302, "test_complete_scenario_vote, status code")
        self.assertEqual(event.eventoption_set.get(pk=1).no_count, 1, "test_complete_scenario_vote, no count")
        self.assertEqual(event.eventoption_set.get(pk=1).yes_count, 0, "test_complete_scenario_vote, yes count")
        self.assertEqual(event.eventoption_set.get(pk=1).maybe_count, 0, "test_complete_scenario_vote, maybe count")