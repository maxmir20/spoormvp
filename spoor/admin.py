from django.contrib import admin

# Register your models here.
from spoor.models import Profile, Credential


class ProfileAdmin(admin.ModelAdmin):
    pass



class CredentialAdmin(admin.ModelAdmin):
    pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Credential, CredentialAdmin)