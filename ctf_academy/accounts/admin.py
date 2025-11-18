from django.contrib import admin
from .models import Category, Challenge, UserProfile, Favorite
from .models import ChallengeProgress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "icon_class")
	prepopulated_fields = {"slug": ("name",)}

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "difficulty", "points", "is_active")
	list_filter = ("category", "difficulty", "is_active")
	search_fields = ("title", "description")
	prepopulated_fields = {"slug": ("title",)}

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "updated_at")

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
	list_display = ("user", "challenge", "created_at")
	list_filter = ("user", "challenge")
	search_fields = ("user__username", "challenge__title")


@admin.register(ChallengeProgress)
class ChallengeProgressAdmin(admin.ModelAdmin):
	list_display = ("user", "challenge", "status", "last_saved_ok", "started_at", "updated_at", "completed_at")
	list_filter = ("status", "last_saved_ok", "updated_at")
	search_fields = ("user__username", "challenge__title")
