import datetime

from django.test import TestCase
from django.utils import timezone

from django.test import Client
from polls.models import Event, EventOption
from django.shortcuts import get_object_or_404
from django.urls import reverse


class EventModelTests(TestCase):
    # def test_was_published_recently_with_future_event(self):
    #     """
    #     was_published_recently() returns False for events whose pub_date
    #     is in the future.
    #     """
    #     time = timezone.now() + datetime.timedelta(days=30)
    #     future_event = Event(pub_date=time)
    #     self.assertIs(future_event.was_published_recently(), False)


    def setUp(self):
        self.client = Client()


    def create_event(self, name):
        event = Event(
                    name=name, description="test Event")
        event.save()
        return event


    def create_EventOptions(self, EventOption_name, event_):
        event_option = EventOption(
            event=event_, event_item_name=EventOption_name,
            event_date="2005-3-3", event_date_from_time="2005-3-3 00:00:00",
            event_date_to_time="2005-3-3 00:00:00", content="2005-3-3 00:00:00"
        )
        event_option.save()
        return event_option


    def test_index_show_polls(self):
        self.create_event("Night Meeting")
        response = self.client.get('/polls/')
        # self.assertEqual(response.context['latest_event_list'][0].name, "Night Meeting", "test_index_show_polls, event")
        self.assertEqual(response.status_code, 200, "Test show Poll Detail, status code")


    def test_detail_show_poll(self):
        event = self.create_event("Night Meeting")
        self.create_EventOptions("Sunday", event)
        self.create_EventOptions("Monday", event)
        response = self.client.get('/polls/1/')
        self.assertContains(response, "Sunday")
        self.assertNotContains(response, "Friday")
        self.assertEqual(response.status_code, 200, "test_detail_show_poll, status code")
    # response = self.client.post(reverse('polls:index'))


    def test_vote_increase_one_vote(self):
        event = self.create_event("Night Meeting")
        self.create_EventOptions("Sunday", event)
        self.create_EventOptions("Monday", event)
        response = self.client.post('/polls/1/vote/', {'eventOption': 2})
        # self.assertEqual(response.status_code, 302, "test_vote_increase_one_vote, status code")
        # self.assertEqual(event.eventoption_set.get(pk=2).votes, 1, "test_vote_increase_one_vote, increasing")
        self.assertEqual(event.eventoption_set.get(pk=1).votes, 0, "test_vote_increase_one_vote, Not changed")


    def test_vote_not_choose_any_option(self):
        event = self.create_event("Night Meeting")
        self.create_EventOptions("Sunday", event)
        response = self.client.post('/polls/1/vote/', {'EventOption': '2'})
        self.assertEqual(response.status_code, 200, "test_vote_not_choose_any_option, status code")
        self.assertContains(response, "You didn&#39;t select a choice.")
        self.assertEqual(event.eventoption_set.get(pk=1).votes, 0, "test_vote_not_choose_any_option")


    def test_system(self):
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