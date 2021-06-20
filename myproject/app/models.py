from django.db import models
from django.contrib.auth.models import User, Permission


# Create your models here.

class RegisteredUser(models.Model):
    GENDER = (
        ('MALE', 'male'),
        ('FEMALE', 'female'),
        ('OTHER', 'other'),
        ('NOT_SAY', 'not_say')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default=1)
    gender = models.CharField(max_length=10, choices=GENDER)
    birth_date = models.DateField()
    mobile_number = models.CharField(max_length=15)


class Train(models.Model):
    name = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    estimated_departure = models.TimeField()
    estimated_arrival = models.TimeField()


class Journey(models.Model):

    class Meta:
        unique_together = ['train', 'journey_date']

    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    journey_date = models.DateField()


class Ticket(models.Model):
    STATUS = (
        ('CONFIRMED', 'confirmed'),
        ('CANCELLED', 'cancelled')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS)
    admit_count = models.IntegerField()
