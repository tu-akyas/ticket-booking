from django.contrib import admin
from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login_user/', views.login_user, name='login_user'),
    path('signup/', views.signup, name='signup')
]