import uuid
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# Create your models here.
from django_cryptography.fields import encrypt

from personal_portfolio import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    live = models.BooleanField(default=True)
    last_track_url = models.URLField(default="")

    def is_live(self):
        """
        returns whether the user is live or not
        """
        return self.live

    def flip_live(self):
        """
        flips status of live to opposite value
        """
        self.live = not self.live
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Credential(models.Model):
    class CredentialType(models.TextChoices):
        SPOTIFY = "SP", _("Spotify")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    type = models.CharField(max_length=2,
                            choices=CredentialType.choices,
                            default=CredentialType.SPOTIFY,)
    encrypted_token = encrypt(models.TextField())
    encrypted_refresh = encrypt(models.TextField())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Playlist(models.Model):
    class PlaylistType(models.TextChoices):
        SPOTIFY = "SP", _("Spotify")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    type = models.CharField(max_length=2,
                            choices=PlaylistType.choices,
                            default=PlaylistType.SPOTIFY, )
    name = models.CharField(max_length=255)
    retrieval_id = models.CharField(max_length=255, unique=True)
    retrieval_url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    artist = models.CharField(max_length=255)
    retrieval_id = models.CharField(max_length=255, unique=True)
    redirect_url = models.URLField(unique=True)








