from django.contrib import admin
from .models import RegisteredUser, Journey, Train, Ticket

# Register your models here.


@admin.register(RegisteredUser, Train, Journey, Ticket)
class AdminModel(admin.ModelAdmin):
    pass