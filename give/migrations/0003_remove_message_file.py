# Generated by Django 5.0.7 on 2024-07-26 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('give', '0002_remove_customuser_blocked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='file',
        ),
    ]
