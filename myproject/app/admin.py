from django.contrib import admin
from .models import RegisteredUser, Journey, Train, Ticket, Feedback

# Register your models here.


@admin.register(RegisteredUser, Train, Journey, Ticket, Feedback)
class AdminModel(admin.ModelAdmin):
    pass
