from django.urls import path
from .views import (
    RegisterView,
    register_page,
    login_page,
    about_page,
    logout_page,
    admin_dashboard_page,
    profile_page,
    MyTokenObtainPairView,
    challenges_page,
    challenge_detail,
    leaderboards_page,
    completed_challenges_page,
    incomplete_challenges_page,
    save_progress,
    toggle_favorite,
    favorites_page,
    update_challenge_status,
    api_mark_inprogress,
    api_mark_complete,
    chatbot_page,
    chatbot_api,
    # ADMIN VIEWS
    admin_users_page,
    admin_users_list,
    admin_user_detail,  # ADD THIS IMPORT
    admin_user_update,
    admin_user_delete,
    admin_user_progress,
    admin_challenge_analytics,
    admin_category_stats,
    admin_export_data,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # REST API ENDPOINTS
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/register/", RegisterView.as_view(), name="register_api"),

    # HTML TEMPLATE PAGES
    path("register", register_page, name="register_page"),
    path("login", login_page, name="login_page"),
    path("logout", logout_page, name="logout_page"),
    path("about/", about_page, name="about_page"),
    path("dashboard/", admin_dashboard_page, name="admin_dashboard_page"),
    path("profile/", profile_page, name="profile_page"),

    # CHALLENGES
    path("challenges/", challenges_page, name="challenges_page"),
    path("leaderboards/", leaderboards_page, name="leaderboards_page"),
    path("challenges/completed/", completed_challenges_page, name="completed_challenges_page"),
    path("challenges/incomplete/", incomplete_challenges_page, name="incomplete_challenges_page"),
    path("challenges/progress/save/<int:challenge_id>/", save_progress, name="save_progress"),
    path("challenges/status/update/<int:challenge_id>/", update_challenge_status, name="update_challenge_status"),
    path("challenges/<slug:slug>/", challenge_detail, name="challenge_detail"),
    path("favorites/", favorites_page, name="favorites_page"),
    path("favorites/toggle/<int:challenge_id>/", toggle_favorite, name="toggle_favorite"),
    
    # TERMINAL SHORTCUTS
    path("inprogress", api_mark_inprogress, name="api_inprogress"),
    path("complete", api_mark_complete, name="api_complete"),

    # CHATBOT
    path("chatbot/", chatbot_page, name="chatbot_page"),
    path("api/chatbot/", chatbot_api, name="chatbot_api"),

    # === ADMIN ENDPOINTS ===
    # User Management
    path("admin/users/", admin_users_page, name="admin_users_page"),
    path("api/admin/users/", admin_users_list, name="admin_users_list"),
    path("api/admin/users/<int:user_id>/", admin_user_detail, name="admin_user_detail"),  # ADD THIS LINE
    path("api/admin/users/<int:user_id>/update/", admin_user_update, name="admin_user_update"),
    path("api/admin/users/<int:user_id>/delete/", admin_user_delete, name="admin_user_delete"),
    
    path("api/admin/users/<int:user_id>/progress/", admin_user_progress, name="admin_user_progress"),
    
    
    # Analytics (View Only)
    path("api/admin/challenges/<int:challenge_id>/analytics/", admin_challenge_analytics, name="admin_challenge_analytics"),
    path("api/admin/category-stats/", admin_category_stats, name="admin_category_stats"),
    path("api/admin/export/", admin_export_data, name="admin_export_data"),
]