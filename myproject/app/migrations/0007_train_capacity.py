# Generated by Django 3.2.4 on 2021-06-28 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_journey_booked_seats'),
    ]

    operations = [
        migrations.AddField(
            model_name='train',
            name='capacity',
            field=models.IntegerField(default=50),
        ),
    ]
