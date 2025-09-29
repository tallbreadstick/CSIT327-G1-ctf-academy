from django.contrib import admin
from .models import User, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	ordering = ("created_at",)
	list_display = ("username", "email", "created_at")
	search_fields = ("username", "email")
	readonly_fields = ("id", "created_at")
	fields = ("id", "username", "email", "password", "created_at")


admin.site.register(Profile)
