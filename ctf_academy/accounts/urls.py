from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # /dashboard/ -> dashboard view (project root includes this file under 'dashboard/')
    path('', views.dashboard, name='dashboard'),

    # explicit per-role pages
    path('general/', views.general, name='general'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),

    # registration (accessible at /dashboard/register/)
    path('register/', views.register, name='register'),

    # Optional: provide login/logout under /dashboard/ (you can also use project-level /accounts/)
    # If you prefer /accounts/login/ provided by django.contrib.auth.urls, keep that in project urls.
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

]
