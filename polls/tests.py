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



    # def test_detail_show_poll(self):
    #     event = self.create_event("Night Meeting")
    #     self.create_EventOptions("Sunday", event)
    #     self.create_EventOptions("Monday", event)
    #     response = self.client.get('/polls/1/')
    #     self.assertContains(response, "Sunday")
    #     self.assertNotContains(response, "Friday")
    #     self.assertEqual(response.status_code, 200, "test_detail_show_poll, status code")
    # # response = self.client.post(reverse('polls:index'))


    # def test_vote_increase_one_vote(self):
    #     event = self.create_event("Night Meeting")
    #     self.create_EventOptions("Sunday", event)
    #     self.create_EventOptions("Monday", event)
    #     response = self.client.post('/polls/1/vote/', {'eventOption': 2})
    #     # self.assertEqual(response.status_code, 302, "test_vote_increase_one_vote, status code")
    #     # self.assertEqual(event.eventoption_set.get(pk=2).votes, 1, "test_vote_increase_one_vote, increasing")
    #     self.assertEqual(event.eventoption_set.get(pk=1).votes, 0, "test_vote_increase_one_vote, Not changed")


    # def test_vote_not_choose_any_option(self):
    #     event = self.create_event("Night Meeting")
    #     self.create_EventOptions("Sunday", event)
    #     response = self.client.post('/polls/1/vote/', {'EventOption': '2'})
    #     self.assertEqual(response.status_code, 200, "test_vote_not_choose_any_option, status code")
    #     self.assertContains(response, "You didn&#39;t select a choice.")
    #     self.assertEqual(event.eventoption_set.get(pk=1).votes, 0, "test_vote_not_choose_any_option")


    def test_system(self):

        user1 = self.create_user("test username1", "test1@test.com")
        user2 = self.create_user("test username2", "test2@test.com")
        creator = self.create_user("test creator username", "testcreator@test.com")
        event = self.create_event("test event", "test description", creator)
        event_option1 = self.create_EventOptions("first test event option", "2019-1-13", "11:45", "2019-1-13",
                                                 "12:00", event)
        event_option2 = self.create_EventOptions("second test event option", "2019-1-13", "12:30", "2019-1-13",
                                                 "13:00", event)


        first_meeting = self.create_event("Night Meeting")
        self.create_EventOptions("Sunday", first_meeting)
        self.create_EventOptions("Monday", first_meeting)

        second_meeting = self.create_event("Control Meeting")
        self.create_EventOptions("Monday", second_meeting)

        third_meeting = self.create_event("Action Meeting")
        self.create_EventOptions("today, at 6", third_meeting)
        self.create_EventOptions("today, at 8", third_meeting)

        forth_meeting = self.create_event("English Meeting")

        response = self.client.get('/polls/')
        self.assertEqual(response.status_code, 200, "test_vote_not_choose_any_option, status code")