# Generated by Django 4.1.3 on 2022-12-12 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0002_alter_booking_experience_alter_booking_room_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="experience_time",
            new_name="experience_time_start",
        ),
        migrations.AddField(
            model_name="booking",
            name="experience_time_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
