# accounts/urls.py

from django.urls import path
from .views import (
    RegisterView,
    register_page,
    login_page,
    about_page,
    logout_page,
    admin_dashboard_page,
    profile_page,
    # --- ADD THIS NEW VIEW ---
    MyTokenObtainPairView,
    challenges_page, # <-- ADD THIS,
    challenge_detail,
    leaderboards_page,
    completed_challenges_page,
    incomplete_challenges_page,
    save_progress,
    toggle_favorite,
    favorites_page,
    update_challenge_status,
)
# --- ADD THESE IMPORTS ---
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # --- MODIFIED REST API ENDPOINTS ---
    # The old LoginView is now removed and replaced by these two endpoints
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/register/", RegisterView.as_view(), name="register_api"),

    # --- HTML TEMPLATE PAGES (Unchanged) ---
    path("register", register_page, name="register_page"),
    path("login", login_page, name="login_page"),
    path("logout", logout_page, name="logout_page"),
    path("about/", about_page, name="about_page"),
    path("dashboard/", admin_dashboard_page, name="admin_dashboard_page"),
    path("profile/", profile_page, name="profile_page"),

    # --- ADD THIS NEW PAGE ---
    path("challenges/", challenges_page, name="challenges_page"),
    path("leaderboards/", leaderboards_page, name="leaderboards_page"),
    path("challenges/completed/", completed_challenges_page, name="completed_challenges_page"),
    path("challenges/incomplete/", incomplete_challenges_page, name="incomplete_challenges_page"),
    path("challenges/progress/save/<int:challenge_id>/", save_progress, name="save_progress"),
    path("challenges/status/update/<int:challenge_id>/", update_challenge_status, name="update_challenge_status"),
    path("challenges/<slug:slug>/", challenge_detail, name="challenge_detail"),
    path("favorites/", favorites_page, name="favorites_page"),
    path("favorites/toggle/<int:challenge_id>/", toggle_favorite, name="toggle_favorite"),
]