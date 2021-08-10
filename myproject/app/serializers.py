from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RegisteredUser


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class RegisteredUserSerializer(serializers.ModelSerializer):
    GENDER = (
        ('MALE', 'male'),
        ('FEMALE', 'female'),
        ('OTHER', 'other'),
        ('NOT_SAY', 'not_say')
    )

    user = UserSerializer(required=True)
    gender = serializers.CharField(required=True, choices=GENDER)
    birth_date = serializers.DateField(required=True)
    mobile_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('user', 'gender', 'birth_date', 'mobile_number')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        gender = validated_data.pop('gender')
        birth_date = validated_data.pop('birth_date')
        mobile_number = validated_data.pop('mobile_number')
        provider = RegisteredUser.objects.update_or_create(
            user=user,
            gender=gender,
            birth_date=birth_date,
            mobile_number=mobile_number
        )
        return provider

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        gender = validated_data.pop('gender')
        birth_date = validated_data.pop('birth_date')
        mobile_number = validated_data.pop('mobile_number')

        instance.gender = gender
        instance.birth_date = birth_date
        instance.mobile_number = mobile_number

        user.username = validated_data.get('username', instance.user.username)
        user.email = validated_data.get('email', user_data['email'])
        user.first_name = user_data.get('first_name', user_data["first_name"])
        user.last_name = user_data.get('last_name', user_data["last_name"])

        user.save()
        instance.save()

        return instance
