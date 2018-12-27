from django.urls import reverse
from .forms import SignUpForm,CreateEventForm, EventOptionForm
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import  HttpResponseRedirect
from .models import Event,EventOption
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def main(request):
    return render(request,'polls/main.html')

def event(request):
    latest_event_list = Event.objects.order_by('name')[:15]
    context = {'latest_event_list': latest_event_list}
    return render(request, 'polls/index.html', context)


def detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'polls/detail.html', {'event': event})


# def vote(request, id):
#     event = get_object_or_404(Event, pk=id)
#     if request.POST:
#         try:
#             selected_eventOption = event.eventoption_set.get(pk=request.POST['eventoption'])
#             selected_eventOption.votes += 1
#             selected_eventOption.save()
#             return HttpResponseRedirect(reverse('polls:results', args=(event.id,)))
#
#         except (KeyError, EventOption.DoesNotExist):
#         # Redisplay the question voting form.
#             return render(request, 'polls/detail.html', {
#             'event': event,
#             'error_message': "You didn't select a choice.",
#             })
#     else:
#         return render(request, 'polls/detail.html',{'event':event})



            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.



def results(request,id):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'polls/results.html', {'event': event})


def new_event(request):
    return render(request,'polls/new_event.html')


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
