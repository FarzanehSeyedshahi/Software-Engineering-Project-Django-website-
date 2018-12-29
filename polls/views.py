from django.urls import reverse
from .forms import SignUpForm,CreateEventForm, EventOptionForm
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponseRedirect
from .models import Event,EventOption, Comment, ReplyComment, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



def main(request):
    return render(request,'polls/main.html')

def event(request):
    latest_event_list = Event.objects.order_by('name')[:15]
    context = {'latest_event_list': latest_event_list}
    return render(request, 'polls/index.html', context)


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


def vote(request, id):
    event = get_object_or_404(Event, pk=id)
    event_options = EventOption.objects.all().filter(event=event)

    all_field_empty = True
    for i in range(len(event_options)):
        event_option_id = 'eventoption' + str(i + 1)
        if request.POST.get(event_option_id, False):
            all_field_empty = False
            choose_option = request.POST[event_option_id]
            save_vote(choose_option, event_options, i)
    if not all_field_empty:
        return HttpResponseRedirect(reverse('polls:results', args=(event.id,)))
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


def replies(request, comment_id):  # todo: user should handled and comment_id for comment_event_option.
    replied_comment = get_object_or_404(Comment, id=comment_id)
    if request.POST:
        text = request.POST['comment']
        user = get_object_or_404(User, email="amin@gmail.com")  # todo amin@gmail.com
        save_reply_to_model(text, replied_comment.event_option, user, replied_comment)
    replies = ReplyComment.objects.filter(replied_comment=replied_comment)
    if replies:
        context = {'replies': replies}
    else:
        comment = get_object_or_404(Comment, id=comment_id)
        context = {'comment': comment}
    return render(request, 'polls/replies.html', context)


def save_comment(request, comment_id):  # todo: user should handled, and url not set to comments.html, and not show replies comment.
    text = request.POST['comment']
    event_option = get_object_or_404(EventOption, id=comment_id)#
    user = get_object_or_404(User, email="amin@gmail.com")  # todo amin@gmail.com
    add_comment_to_model(text, event_option, user)
    context = {'event_option': event_option}
    return render(request, 'polls/comments.html', context)


def results(request,id):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'polls/results.html', {'event': event})


def new_event(request):
    return render(request, 'polls/new_event.html')


def create_new_event(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        #formset = EventForm(request.POST)
        if [form.is_valid()]:
            event = form.save()
            #formset_ = formset.save()
            event.save()
            #formset_.save()
            return redirect('polls:add_option')
    else:
        form = CreateEventForm()
        #formset =EventOption()
        return render(request, 'polls/new_event.html', {'form': form})

def add_option(request):
    if request.method == 'POST':
        formset = EventOptionForm(request.POST)
        if [formset.is_valid()]:
            event_option = formset.save()
            event_option.save()
            return redirect('polls:add_option')
    else:
        formset = EventOptionForm()
        return render(request, 'polls/addoption.html', {'formset': formset})


def signup(request,template_name, next_page):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('polls:main')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view (request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        redirect('polls:main')
    else:
        print('invalid Login')

def logout_view(request):
    logout(request)
    redirect('polls:rest_framework:login')
