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
    path('train/<int:train_id>/booking/', views.booking_journey, name='booking'),
    path('tickets/', views.tickets, name='tickets'),
    path('ticket/<int:ticket_id>/', views.ticket_details, name='ticket_details'),
    path('ticket/<int:ticket_id>/cancel', views.cancel_ticket, name='cancel_ticket'),
    path('profile/', views.user_profile, name='user_profile'),
    path('feedback/', views.feedbacks, name='feedbacks')

]