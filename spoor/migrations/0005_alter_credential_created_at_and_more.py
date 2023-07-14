# Generated by Django 4.2.3 on 2023-07-13 12:14

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('spoor', '0004_track_profile_last_track_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 13, 12, 14, 49, 533352)),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 13, 12, 14, 49, 534064)),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='id',
            field=models.UUIDField(default=uuid.UUID('003feb5d-f9c5-4d13-b44e-7bb538768948'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='track',
            name='id',
            field=models.UUIDField(default=uuid.UUID('b3236ebe-5f76-4b37-abe2-7ded55366b83'), editable=False, primary_key=True, serialize=False),
        ),
    ]
