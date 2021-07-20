from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout, decorators
from .forms import UserForm, RegisteredUserForm, BookingForm
from django.template import RequestContext
from .models import Train, Journey, Ticket, RegisteredUser, Feedback
from datetime import date
from dateutil.relativedelta import relativedelta


# Create your views here.
def index(request):
    return HttpResponseRedirect('home')


def home(request):
    if request.user.is_authenticated:
        context = {'user': request.user}
        template = 'app/home_user.html'
    else:
        context = {}
        template = 'app/home.html'
    return render(request, template, context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'app/home_user.html', {"user": user})
            else:
                return render(request, 'app/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'app/login.html', {'error_message': 'Invalid login'})
    return render(request, 'app/login.html')


def signup(request):
    user_form = UserForm(request.POST or None)
    registered_user_form = RegisteredUserForm(request.POST or None)
    if user_form.is_valid() and registered_user_form.is_valid():
        user = user_form.save(commit=False)
        register_user = registered_user_form.save(commit=False)
        register_user.user = user

        username = user_form.cleaned_data['username']
        password = user_form.cleaned_data['password']
        user.set_password(password)
        user.save()
        register_user.save()

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'app/home_user.html', {'user': user})
    context = {
        "user_form": user_form,
        "registered_user_form": registered_user_form
    }
    return render(request, 'app/signup.html', context)


def logout_user(request):
    logout(request)
    return render(request, 'app/login.html', {})


def all_trains(request):
    all_trains = Train.objects.all()
    if request.user.is_authenticated:
        context = {'user': request.user, 'all_trains': all_trains}
        template = 'app/all_trains_user.html'
    else:
        context = {'all_trains': all_trains}
        template = 'app/all_trains.html'
    return render(request, template, context)


def train_detail(request, train_id):
    train = get_object_or_404(Train, pk=train_id)
    if request.user.is_authenticated:
        context = {'user': request.user, 'train': train}
        template = 'app/train_details_user.html'
    else:
        context = {'train': train}
        template = 'app/train_details.html'
    return render(request, template, context)


def booking_journey(request, train_id):
    if not request.user.is_authenticated:
        return render(request, 'app/login.html')

    train = get_object_or_404(Train, pk=train_id)

    booking_form = BookingForm(request.POST or None)
    template = 'app/booking.html'

    if booking_form.is_valid():

        journey_date = booking_form.cleaned_data.get("journey_date")
        admit_count = booking_form.cleaned_data.get("admit_count")

        journey_filter = Journey.objects.filter(train=train, journey_date=journey_date)

        if len(journey_filter) == 0:
            journey = Journey(train=train, journey_date=journey_date)
            journey.save()
        else:
            journey = journey_filter[0]

        available_seats = train.capacity - journey.booked_seats
        if journey_date <= date.today():
            error_message = f"Sorry!! Invalid date, Bookings are closed 1 day before the journey"
            context = {
                'form': booking_form,
                'train': train,
                'error_message': error_message
            }
            return render(request, template, context)
        elif admit_count > available_seats:
            error_message = f"Sorry!! We have only {available_seats} available seats for <<{journey}>>," \
                            f" We cannot offer {admit_count} seats at this moment, " \
                            f" Please Try booking on a different date or " \
                            f"Try again later, in case of any cancellations you may get your tickets"
            context = {
                'form': booking_form,
                'train': train,
                'error_message': error_message
            }
            return render(request, template, context)

        ticket = Ticket(
            user=request.user,
            journey=journey,
            status='CONFIRMED',
            admit_count=admit_count
        )

        journey.booked_seats += admit_count

        ticket.save()
        journey.save()

        # Write a success message and develop booking_success HTML
        success_message = f"You have sucessfully booked your ticket,  <<Ticket No: {ticket.pk}>>"
        context = {
            "user": request.user,
            "train": train,
            "ticket": ticket,
            "success_message": success_message
        }
        return render(request, template, context)

    context = {
        "form": booking_form,
        "train": train
    }
    return render(request, template, context)


def tickets(request):
    if not request.user.is_authenticated:
        return render(request, 'app/login.html')

    user_tickets = Ticket.objects.filter(user=request.user)
    user_tickets = user_tickets[::-1]

    template = 'app/tickets.html'
    context = {
        "user_tickets": user_tickets
    }

    return render(request, template, context)


def ticket_details(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    template = 'app/ticket_details.html'
    context = {'ticket': ticket}

    return render(request, template, context)


def cancel_ticket(request, ticket_id):
    if not request.user.is_authenticated:
        return render(request, 'app/login.html')

    today_date = date.today()
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    journey = ticket.journey
    template = 'app/ticket_details.html'

    if ticket.journey.journey_date > today_date:
        journey.booked_seats -= ticket.admit_count
        ticket.status = "CANCELLED"

        journey.save()
        ticket.save()

        context = {
            'ticket': ticket,
            'success_message': f'Ticket# {ticket_id} is cancelled'
        }
        return render(request, template, context)

    error_message = "Sorry! You cannot cancel today's journey or a completed journey."
    context = {
        'ticket': ticket,
        'error_message': error_message
    }
    return render(request, template, context)


def user_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'app/login.html')

    template = 'app/profile.html'

    reg_user = get_object_or_404(RegisteredUser, user=request.user)
    user_age = f"{relativedelta(date.today(), reg_user.birth_date).years} years"

    context = {"reg_user": reg_user, "user_age": user_age}

    return render(request, template, context)


def feedbacks(request):
    feedback_received = False
    if request.method == 'POST':
        name = request.POST.get('Name')
        email = request.POST.get('Email')
        text = request.POST.get('Feedback')

        feedback = Feedback(name=name, email=email, text=text)
        feedback.save()

        feedback_received = True
        return render(request, 'app/home.html', {'feedback_received':feedback_received})
    return render(request, 'app/home.html', {'feedback_received':feedback_received})
