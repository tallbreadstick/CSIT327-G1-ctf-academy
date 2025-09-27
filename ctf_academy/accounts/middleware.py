# accounts/middleware.py
from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
import time

class AutoLogoutMiddleware:
    """
    Auto-logout users after SESSION_COOKIE_AGE seconds of inactivity
    and display a message.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = int(time.time())  # current time in seconds
            last_activity = request.session.get('last_activity')

            if last_activity:
                elapsed = now - last_activity
                if elapsed > settings.SESSION_COOKIE_AGE:
                    auth.logout(request)
                    messages.info(request, "You have been logged out due to inactivity.")
                    return redirect(settings.LOGIN_URL)

            # update last_activity every request
            request.session['last_activity'] = now

        response = self.get_response(request)
        return response
