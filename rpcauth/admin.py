from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ["name", "username", "datatracker_subject_id"]
    list_display = ["name", "username", "datatracker_subject_id"]


admin.site.register(User, UserAdmin)
