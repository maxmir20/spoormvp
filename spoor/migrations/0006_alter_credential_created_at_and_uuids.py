# Generated by Django 4.2.3 on 2023-07-16 02:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('spoor', '0005_alter_credential_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='id',
            field=models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='track',
            name='id',
            field=models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, serialize=False),
        ),
    ]
