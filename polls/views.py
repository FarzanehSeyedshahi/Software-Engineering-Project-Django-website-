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
    # print(even)
    # user = User()
    # busy = BusyDate.objects.all()
    # for i in busy:
    #     print("***", i.start_time, i.user, i.name, i.day)
    #     print("__________________")
    return render(request, 'polls/main.html')

def event(request):
    events = ParticipateIn.objects.filter(participant_email=request.user.email) #todo: change this name
    # latest_event_list = Event.objects.order_by('name')[:15]
    # print("**", latest_event_list[0].event.name)
    context = {'events': events}
    # print(len(events))
    return render(request, 'polls/index.html', context)

def own_event(request):
    print("***")
    creator_user = User.objects.get(username=request.user.username)
    events = Event.objects.filter(creator=creator_user) #todo: change this name
    context = {'events': events}
    # print(events[0])
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
    print(choose_option, event_options[i].to_time, user)
    print(choose_option, event_options[i].from_date, user)
    print("&&&&&&&^^^*")
    if choose_option != 1:
        return False
    else:
        print("^#%")
        busyDates = BusyDate.objects.filter(user=user)
        # print(busyDates[0].start_time, busyDates.end_time)
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
    print("herre")

    all_field_empty = True
    overlap = False
    for i in range(len(event_options)):
        event_option_id = 'eventoption' + str(event_options[i].id)
        print(event_option_id)
        if request.POST.get(event_option_id, False):
            all_field_empty = False
            choose_option = request.POST[event_option_id]
            save_vote(choose_option, event_options, i)
            if has_overlap(int(choose_option), event_options, i, user):
                overlap = True
    if not all_field_empty:
        # if not overlap:
        return HttpResponseRedirect(reverse('polls:results', args=(event.id, int(overlap))))
        # else:
        #     return HttpResponseRedirect(reverse('polls:results', args=(event.id, 1)))
        #     return render(request, 'polls/detail.html', {
        #     'event': event,
        #     'error_message': "Your choise has ",
        # })
    else:
        return render(request, 'polls/detail.html', {
            'event': event,
            'error_message': "You didn't select a choice.",
        })


def comments(request, option_id):
    event_option = get_object_or_404(EventOption, id=option_id)
    comments = Comment.objects.filter(event_option=event_option)
    # if not comments:
    return render(request, 'polls/comments.html', {'event_option': event_option})
    # else:
    #     context = {'comments': comments}
    #     return render(request, 'polls/comments.html', context)


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


#todo: request.user.email
def replies(request, comment_id):  # todo: user should handled and comment_id for comment_event_option.
    replied_comment = get_object_or_404(Comment, id=comment_id)
    if request.POST:
        text = request.POST['comment']
        user = get_object_or_404(User, email=request.user.email)  # todo amin@gmail.com
        save_reply_to_model(text, replied_comment.event_option, user, replied_comment)
    replies = ReplyComment.objects.filter(replied_comment=replied_comment)
    if replies:
        context = {'replies': replies}
    else:
        comment = get_object_or_404(Comment, id=comment_id)
        context = {'comment': comment}
    return render(request, 'polls/replies.html', context)


#todo: request.user.email
def save_comment(request, comment_id):  # todo: user should handled, and url not set to comments.html, and not show replies comment.
    text = request.POST['comment']
    print ('HI')
    event_option = get_object_or_404(EventOption, id=comment_id)
    user = get_object_or_404(User, email=request.user.email)  # todo amin@gmail.com
    add_comment_to_model(text, event_option, user)
    context = {'event_option': event_option}
    return render(request, 'polls/comments.html', context)


def results(request,id, overlap):
    # print(overlap)
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
            # return redirect('polls:add_option')
            # return render(request, 'polls/addoption.html', {'event': event})
    else:
        form = CreateEventForm()
        return render(request, 'polls/new_event.html', {'form': form})


def add_option(request, event_id):
    event = Event.objects.get(id=event_id)
    print("event_id:", event_id)
    if request.method == 'POST':
        formset = EventOptionForm(request.POST)
        if [formset.is_valid()]:
            event_option = formset.save(commit=False)
            event_option.event = event
            event_option.save()
            # return redirect('polls:add_option')
            return HttpResponseRedirect(reverse('polls:add_option', args=(event.id,)))
    else:
        formset = EventOptionForm()
        return render(request, 'polls/addoption.html', {'formset': formset, 'event': event})


def send_email_to_participates(participate_emails, event, email_text=""):
    print("in ")
    subject = event.name
    if email_text == "":
        email_body = "Hello!\n" + event.creator.email + " has just made a new poll in AS-IS Meeting Scheduler and invited " \
                                                        "you to vote for it.\n" + event.name + "\n" + event.description +\
                     "\n\nVote before it closed."
    else:
        email_body = email_text
    email = EmailMessage(subject, email_body, 'asis.meetingscheduler@gmail.com', participate_emails)
    email.send()
    print("maybe email sent:)")
    return


def save_participate_to_model(participate_emails, event):
    for participate_email in participate_emails:
        participateIn = ParticipateIn(
            participant_email=participate_email, event=event
        )
        print("Saved...")
        participateIn.save()
    send_email_to_participates(participate_emails, event)


def save_participate(request, event_id):
    event = Event.objects.get(id=event_id)
    i = 1
    print()
    participate_emails = []
    while True:
        participate_number = 'participate' + str(i)
        # print(participate_number)
        # print(request.POST[participate_number])
        if not(participate_number in request.POST):
        #     print("yessssssss")
        # if request.POST.get(participate_number, False):
            print("HERE")
            break
        else:
            print("in else")
            participate_emails.append(request.POST[participate_number])
        i = i + 1
    save_participate_to_model(participate_emails, event)
    return render(request, 'polls/main.html')


def add_participate(request, event_id):
    event = Event.objects.get(id=event_id)
    print("IIII")
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
    print(":))")
    for participateIn in participateIns:
        user = User.objects.get(email=participateIn.participant_email)
        event_option_date = event_option.from_date
        while True:
            busyDate = BusyDate(user=user, day=event_option.from_date,
                                start_time=event_option.from_time, end_time=event_option.to_time,
                                name=event.name
            )
            busyDate.save()
            event_option_date += timedelta(days=event.repeating_day)
            print(":D", event_option_date, event.ending_date, event.repeating_day)
            if event_option_date.isoformat() > event.ending_date.isoformat():
                break


def finish_event(request, event_id):#todo:
    print("III", request.POST['eventoption'])
    event = get_object_or_404(Event, id=event_id)
    event_option_id = request.POST['eventoption']
    event_option = get_object_or_404(EventOption, id=event_option_id)
    save_event_result_on_model(event, event_option)
    save_busy_time_result_on_model(event, event_option)
    return render(request, 'polls/owndetail.html', {'event': event})


def reactive_event(request, event_id):
    ###
    event = get_object_or_404(Event, id=event_id)
    print("***", event.holding_date_from, event.holding_date_to)
    ###
    email_text = request.POST['reactive_email'] #todo: this is email_text;
    event = get_object_or_404(Event, id=event_id)
    event.active_status = 1
    event.save()
    participate_emails = []
    participates = ParticipateIn.objects.filter(event=event)
    print("Here", email_text) #todo, this
    for participate in participates:
        participate_emails.append(participate.participant_email)
    send_email_to_participates(participate_emails, event, email_text) #todo: Farzane zirak.
    return render(request, 'polls/owndetail.html', {'event': event})


# def signup(request,template_name, next_page):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#             user.refresh_from_db()  # load the profile instance created by the signal
#             user.save()
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=user.username, password=raw_password)
#             login(request, user)
#             return redirect('polls:main')
#     else:
#         form = SignUpForm()
#     return render(request, 'registration/signup.html', {'form': form})


# def login_view (request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         redirect('polls:main')
#     else:
#         print('invalid Login')
#
# def logout_view(request):
#     logout(request)
#     redirect('polls:rest_framework:login')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('polls:main')
    else:
        form = UserCreationForm()
    return render(request,'registration/signup.html',{'form':form})

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