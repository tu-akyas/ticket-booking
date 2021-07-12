from django.db import models
from django.contrib.auth.models import User, Permission


# Create your models here.

class RegisteredUser(models.Model):
    GENDER = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('NOT_SAY', 'I prefer not to say')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    birth_date = models.DateField()
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user}"


class Train(models.Model):
    name = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    estimated_departure = models.TimeField()
    estimated_arrival = models.TimeField()
    operated_days = models.CharField(max_length=15, default="All Days")
    ticket_price = models.IntegerField(default=10)
    capacity = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.name} ({self.pk})"


class Journey(models.Model):

    class Meta:
        unique_together = ['train', 'journey_date']

    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    journey_date = models.DateField()
    booked_seats = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.train} - {self.journey_date}"


class Ticket(models.Model):
    STATUS = (
        ('CONFIRMED', 'confirmed'),
        ('CANCELLED', 'cancelled')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS)
    admit_count = models.IntegerField()

    def __str__(self):
        return f"Ticket# {self.pk} | {self.journey} | {self.user} | \n Admit: {self.admit_count} | {self.status}"
