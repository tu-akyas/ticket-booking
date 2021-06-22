from django import forms
from django.contrib.auth.models import User
from .models import RegisteredUser
from datetime import date


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(label="Email Id")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class RegisteredUserForm(forms.ModelForm):
    current_year = date.today().year
    YEAR_CHOICE = range((current_year-100), current_year)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=YEAR_CHOICE), label="D.O.B")
    mobile_number = forms.CharField(widget=forms.NumberInput, label="Mob. No.")


    class Meta:
        model = RegisteredUser
        fields = ['gender', 'birth_date', 'mobile_number']
