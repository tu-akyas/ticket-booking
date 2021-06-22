from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout, decorators
from .forms import UserForm, RegisteredUserForm
from django.template import RequestContext
from .models import Train


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
                return render(request, 'app/home_user.html', {'user':user})
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

def booking(request, train_id):
    if not request.user.is_authenticated:
        return render(request, 'app/login.html')
    train = get_object_or_404(Train, pk=train_id)
    return render(request, 'app/booking.html', {})

