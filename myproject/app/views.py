from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout, decorators
from .forms import UserForm, RegisteredUserForm, BookingForm
from django.template import RequestContext
from .models import Train, Journey, Ticket, RegisteredUser, Feedback
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings


# Create your views here.
def index(request):
    return HttpResponseRedirect('home')


def home(request, feedback_received=False):
    if request.user.is_authenticated:
        context = {'user': request.user}
        template = 'app/home_user.html'
    else:
        context = {}
        template = 'app/home.html'

    frequent_train = get_frequent_train()
    print(f"Inside View Frequent_train:{frequent_train}")
    user_frequent_train = get_frequent_train(user=request.user)
    print(f"Inside View User Frequent_train:{user_frequent_train}")

    suggested_trains = [
        {
            "train": Train.objects.get(id=1),
            "description": "This is Our First train operated by us! First is always best"
        },

        {
            "train": Train.objects.get(id=3),
            "description": "This is a fantasy Journey to Hogwarts inspired from Harry Potter! Enjoy your journey"
        },

        {
            "train": Train.objects.get(id=5),
            "description": "This is a journey to a fantasy Polar Island where you can play with snowman!"
        }
    ]

    context.update({
        "suggested_trains": suggested_trains,
        "frequent_train": frequent_train,
        "user_frequent_train": user_frequent_train,
        "feedback_received": feedback_received
    })

    return render(request, template, context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return home(request)
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

        send_user_registration_mail(user=user)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return home(request)
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
        send_booking_confirmation_email(ticket)

        # Write a success message and develop booking_success HTML
        success_message = f"You have sucessfully booked your ticket,  <<Ticket No: {ticket.pk}>>"
        context = {
            "user": request.user,
            "form": booking_form,
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

    for ticket in user_tickets:
        if ticket.status == 'CONFIRMED' and ticket.journey.journey_date <= date.today():
            ticket.status = 'COMPLETED'
            ticket.save()
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
        send_booking_cancellation_email(ticket=ticket)

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
    if request.method == 'POST':
        name = request.POST.get('Name')
        email = request.POST.get('Email')
        text = request.POST.get('Feedback')

        feedback = Feedback(name=name, email=email, text=text)
        feedback.save()

        send_feedback_notification(feedback)

        feedback_received = True
    return home(request, feedback_received=feedback_received)


# User defined functions not related to views. These functions are used in some logics
def get_frequent_train(user=None):
    '''
        1. Returns most booked trains in the system
        2. Returns most booked trains by the user
    '''
    if user:
        ticket_objects = Ticket.objects.all()
    else:
        ticket_objects = Ticket.objects.filter(user=user)

    booked_trains = []
    for ticket in ticket_objects:
        booked_trains.append(ticket.journey.train)

    if len(booked_trains) <= 0:
        for train in Train.objects.all():
            booked_trains.append(train)

    # returns the element has most occurence in the list
    frequently_booked_train = max(set(booked_trains), key=booked_trains.count)
    print(f"inside function {frequently_booked_train}")

    return frequently_booked_train


def send_simple_email(subject, email_to, template, context):
    body = ""
    html_message = loader.render_to_string(template_name=template, context=context)
    send_mail(subject=subject, message=body, from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email_to], html_message=html_message)
    return None


def send_user_registration_mail(user):
    template = 'app/registration_email.html'
    context = {'user': user}
    subject = "Akyas Railways| Registration Successful"
    email_to = user.email
    send_simple_email(
        subject=subject,
        context=context,
        email_to=email_to,
        template=template
    )
    return None


def send_booking_confirmation_email(ticket):
    template = 'app/ticket_booking_email.html'
    context = {'ticket': ticket}
    subject = f"{ticket} booking confirmation"
    email_to = ticket.user.email
    send_simple_email(
        subject=subject,
        context=context,
        email_to=email_to,
        template=template
    )
    return None


def send_booking_cancellation_email(ticket):
    template = 'app/ticket_cancellation_email.html'
    context = {'ticket': ticket}
    subject = f"Booking Cancelled {ticket}"
    email_to = ticket.user.email
    send_simple_email(
        subject=subject,
        context=context,
        email_to=email_to,
        template=template
    )
    return None


def send_feedback_notification(feedback):
    template = 'app/feedback_email.html'
    context = {'feedback': feedback}
    subject = f"Feedback #{feedback.pk} received from {feedback.name}"
    email_to = "tu.akyas+testing@gmail.com"
    send_simple_email(
        subject=subject,
        context=context,
        email_to=email_to,
        template=template
    )
    return None
