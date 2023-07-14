from django.contrib import admin

# Register your models here.
from spoor.models import Profile, Credential, Track, Playlist


class ProfileAdmin(admin.ModelAdmin):
    pass



class CredentialAdmin(admin.ModelAdmin):
    pass


class PlaylistAdmin(admin.ModelAdmin):
    pass


class TrackAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Credential, CredentialAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Playlist, PlaylistAdmin)