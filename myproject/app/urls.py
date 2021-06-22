from django.contrib import admin
from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('signup/', views.signup, name='signup'),
    path('all_trains/', views.all_trains, name='all_trains'),
    path('train/<int:train_id>', views.train_detail, name='train_detail'),
    path('train/<int:train_id>/booking', views.booking, name='booking')

]