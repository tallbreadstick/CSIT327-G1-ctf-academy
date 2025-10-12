# accounts/urls.py

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    register_page,
    login_page,
    about_page,
    logout_page,
    admin_dashboard_page # Don't forget to import your new admin dashboard view
)

urlpatterns = [
    # REST API endpoints
    path("api/register/", RegisterView.as_view(), name="register_api"),
    path("api/login/", LoginView.as_view(), name="login_api"),

    # HTML Template Pages
    path("register", register_page, name="register_page"),
    path("login", login_page, name="login_page"),
    path("logout", logout_page, name="logout_page"),
    path("about", about_page, name="about_page"),
    path("dashboard", admin_dashboard_page, name="admin_dashboard_page"),
]