from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.contrib.auth import authenticate, login


# Create your views here.

def index(request):
    return HttpResponseRedirect('home/')


def home(request):
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
                return render(request, 'app/index.html', {})
            else:
                return render(request, 'app/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'app/login.html', {'error_message': 'Invalid login'})
    return render(request, 'app/login.html')


def signup(request):
    context = {}
    template = 'app/signup.html'
    return render(request, template, context)
