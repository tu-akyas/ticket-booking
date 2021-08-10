from django import forms
from django.contrib.auth.models import User
from .models import RegisteredUser
from datetime import date, timedelta


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(label="Email Id", required=True)
    first_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','username', 'password']


class RegisteredUserForm(forms.ModelForm):
    current_year = date.today().year
    YEAR_CHOICE = range((current_year - 100), current_year)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=YEAR_CHOICE), label="D.O.B")
    mobile_number = forms.CharField(widget=forms.NumberInput, label="Mob. No.")

    class Meta:
        model = RegisteredUser
        fields = ['gender', 'birth_date', 'mobile_number']


class BookingForm(forms.Form):
    default_date = date.today() + timedelta(days=1)
    journey_date = forms.DateField(
        label="Select a Date of Journey",
        widget=forms.SelectDateWidget,
        initial=default_date
    )
    admit_count = forms.IntegerField(
        label="No. Of. Passengers",
        min_value=1,
        initial=1
    )
