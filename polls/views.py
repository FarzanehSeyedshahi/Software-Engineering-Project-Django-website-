from datetime import timedelta

from django.urls import reverse
from .forms import UserLoginForm,UserRegisterForm,CreateEventForm, EventOptionForm
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import  HttpResponseRedirect
from .models import Event,EventOption
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth import (authenticate, get_user_model, login,logout)
from django.http import HttpResponseRedirect
from .models import Event,EventOption, Comment, ReplyComment, ParticipateIn, BusyDate
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


@login_required
def main(request):
    busy_date = BusyDate.objects.filter(user=request.user)
    context = {'busy_date': busy_date}
    return render(request, 'polls/main.html', context)


def event(request):
    events = ParticipateIn.objects.filter(participant_email=request.user.email)
    context = {'events': events}
    return render(request, 'polls/index.html', context)


def own_event(request):
    creator_user = User.objects.get(username=request.user.username)
    events = Event.objects.filter(creator=creator_user)
    context = {'events': events}
    return render(request, 'polls/index.html', context)


def own_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'polls/owndetail.html', {'event': event})


def detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'polls/detail.html', {'event': event})


def save_vote(choose_option, event_options, i):
    if choose_option == '1':
        event_options[i].yes_count += 1
    elif choose_option == '2':
        event_options[i].no_count += 1
    else:
        event_options[i].maybe_count += 1
    event_options[i].save()


def has_overlap(choose_option, event_options, i, user):
    if choose_option != 1:
        return False
    else:
        busyDates = BusyDate.objects.filter(user=user)
        for busyDate in busyDates:
            if busyDate.day != event_options[i].from_date:
                continue
            if (busyDate.start_time.isoformat() < event_options[i].to_time.isoformat() and busyDate.start_time.isoformat() > event_options[i].from_time.isoformat()) or\
                (busyDate.start_time.isoformat() < event_options[i].from_time.isoformat() and busyDate.end_time.isoformat() > event_options[i].to_time.isoformat()) or\
                (busyDate.end_time.isoformat() > event_options[i].from_time.isoformat() and busyDate.end_time.isoformat() < event_options[i].to_time.isoformat()) or\
                (busyDate.start_time.isoformat() > event_options[i].from_time.isoformat() and busyDate.end_time.isoformat() < event_options[i].to_time.isoformat()):
                    return True
        return False


def vote(request, id):
    event = get_object_or_404(Event, pk=id)
    event_options = EventOption.objects.all().filter(event=event)
    user = User.objects.get(username=request.user.username)

    all_field_empty = True
    overlap = False
    for i in range(len(event_options)):
        event_option_id = 'eventoption' + str(event_options[i].id)
        if request.POST.get(event_option_id, False):
            all_field_empty = False
            choose_option = request.POST[event_option_id]
            save_vote(choose_option, event_options, i)
            if has_overlap(int(choose_option), event_options, i, user):
                overlap = True
    if not all_field_empty:
        return HttpResponseRedirect(reverse('polls:results', args=(event.id, int(overlap))))
    else:
        return render(request, 'polls/detail.html', {
            'event': event,
            'error_message': "You didn't select a choice.",
        })


def comments(request, option_id):
    event_option = get_object_or_404(EventOption, id=option_id)
    comments = Comment.objects.filter(event_option=event_option)
    return render(request, 'polls/comments.html', {'event_option': event_option})


def add_comment_to_model(text, event_option, user):
    comment = Comment(
        text=text, event_option=event_option,
        commenter=user
    )
    comment.save()
    return comment


def save_reply_to_model(text, event_option, user, replied_comment):
    comment = add_comment_to_model(text, event_option, user)
    reply_comment = ReplyComment(
        commenter=user, new_comment=comment, replied_comment=replied_comment
    )
    reply_comment.save()


def replies(request, comment_id):
    replied_comment = get_object_or_404(Comment, id=comment_id)
    if request.POST:
        text = request.POST['comment']
        user = get_object_or_404(User, email=request.user.email)
        save_reply_to_model(text, replied_comment.event_option, user, replied_comment)
    replies = ReplyComment.objects.filter(replied_comment=replied_comment)
    if replies:
        context = {'replies': replies}
    else:
        comment = get_object_or_404(Comment, id=comment_id)
        context = {'comment': comment}
    return render(request, 'polls/replies.html', context)


def save_comment(request, comment_id):
    text = request.POST['comment']
    event_option = get_object_or_404(EventOption, id=comment_id)
    user = get_object_or_404(User, email=request.user.email)
    add_comment_to_model(text, event_option, user)
    context = {'event_option': event_option}
    return render(request, 'polls/comments.html', context)


def results(request, id, overlap):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'polls/results.html', {'event': event, 'overlap': overlap})


def new_event(request):
    return render(request, 'polls/new_event.html')


def create_new_event(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if [form.is_valid()]:
            event = form.save(commit=False)
            user = User.objects.get(username=request.user.username)
            event.creator = user
            event.save()
            return HttpResponseRedirect(reverse('polls:add_option', args=(event.id,)))
    else:
        form = CreateEventForm()
        return render(request, 'polls/new_event.html', {'form': form})


def add_option(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        formset = EventOptionForm(request.POST)
        if [formset.is_valid()]:
            event_option = formset.save(commit=False)
            event_option.event = event
            event_option.save()
            return HttpResponseRedirect(reverse('polls:add_option', args=(event.id,)))
    else:
        formset = EventOptionForm()
        return render(request, 'polls/addoption.html', {'formset': formset, 'event': event})


def send_email_to_participates(participate_emails, event, email_text=""):
    subject = event.name
    if email_text == "":
        email_body = "Hello!\n" + event.creator.email + " has just made a new poll in AS-IS Meeting Scheduler and invited " \
                                                        "you to vote for it.\n" + event.name + "\n" + event.description +\
                     "\n\nVote before it closed."
    else:
        email_body = email_text
    email = EmailMessage(subject, email_body, 'asis.meetingscheduler@gmail.com', participate_emails)
    # email.send()
    return


def save_participate_to_model(participate_emails, event):
    for participate_email in participate_emails:
        participateIn = ParticipateIn(
            participant_email=participate_email, event=event
        )
        participateIn.save()
    # send_email_to_participates(participate_emails, event)


def save_participate(request, event_id):
    event = Event.objects.get(id=event_id)
    i = 1
    participate_emails = []
    while True:
        participate_number = 'participate' + str(i)
        if not(participate_number in request.POST):
            break
        else:
            participate_emails.append(request.POST[participate_number])
        i = i + 1
    save_participate_to_model(participate_emails, event)
    return render(request, 'polls/main.html')


def add_participate(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, 'polls/addparticipate.html', {'event': event})


def save_event_result_on_model(event, event_option):
    event.active_status = 0
    event.holding_date_from = event_option.from_date
    event.holding_time_from = event_option.from_time
    event.holding_date_to = event_option.to_date
    event.holding_time_to = event_option.to_time
    event.save()


def save_busy_time_result_on_model(event, event_option):
    participateIns = ParticipateIn.objects.filter(event=event)
    for participateIn in participateIns:
        user = User.objects.get(email=participateIn.participant_email)
        event_option_date = event_option.from_date
        while True:
            busyDate = BusyDate(user=user, day=event_option_date,
                                start_time=event_option.from_time, end_time=event_option.to_time,
                                name=event.name
            )
            busyDate.save()
            event_option_date += timedelta(days=event.repeating_day)
            if event_option_date.isoformat() > event.ending_date.isoformat():
                break


def finish_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event_option_id = request.POST['eventoption']
    event_option = get_object_or_404(EventOption, id=event_option_id)
    save_event_result_on_model(event, event_option)
    save_busy_time_result_on_model(event, event_option)
    return render(request, 'polls/owndetail.html', {'event': event})


def reactive_event(request, event_id):
    email_text = request.POST['reactive_email']
    event = get_object_or_404(Event, id=event_id)
    event.active_status = 1
    event.save()
    participate_emails = []
    participates = ParticipateIn.objects.filter(event=event)
    for participate in participates:
        participate_emails.append(participate.participant_email)
    send_email_to_participates(participate_emails, event, email_text)
    return render(request, 'polls/owndetail.html', {'event': event})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('polls:main')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html',{'form':form})


def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username= username, password = password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect("/")
    context = {
        'form': form,
    }
    return render(request, "registration/login.html", context)


def register_view(request):
    next = request.GET.get('next')
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username = user.username, password = password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect("/")
    context = {
        'form': form,
    }
    return render(request, "registration/signup.html", context)


def logout_view(request):
    logout(request)
    return redirect('/')