from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # this includes the accounts app under /dashboard/
    path('dashboard/', include('accounts.urls')),

    # include Django's auth under /accounts/ (optional but useful)
    path('accounts/', include('django.contrib.auth.urls')),

    # redirect root "/" to the login page:
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]
