# Generated by Django 4.1.7 on 2023-03-03 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0003_rename_volunteer_request_volunteer'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='is_finished',
            field=models.BooleanField(default=False),
        ),
    ]