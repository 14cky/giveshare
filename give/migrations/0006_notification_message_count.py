# Generated by Django 5.0.7 on 2024-08-19 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('give', '0005_profile_email_notifications_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message_count',
            field=models.IntegerField(default=0),
        ),
    ]
