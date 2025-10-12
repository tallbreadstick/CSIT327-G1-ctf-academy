"""
URL configuration for ctf_academy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# ctf_academy/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home_page, name="home"),
    path("", include("accounts.urls")),
]

# Add this line to register your custom 404 handler
handler404 = 'accounts.views.handler404_view'