from django.urls import path
from .views import RegisterView, LoginView, register_page, login_page

urlpatterns = [
    # REST API endpoints
    path("register/", RegisterView.as_view(), name="register_api"),
    path("login/", LoginView.as_view(), name="login_api"),

    # HTML form pages
    path("page/register/", register_page, name="register_page"),
    path("page/login/", login_page, name="login_page"),
]
