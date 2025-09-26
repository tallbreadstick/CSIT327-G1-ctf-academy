from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def register(request):
    """Registration page -> after successful registration redirect to login."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")   # uses the named 'login' route (django.contrib.auth)
    else:
        form = UserCreationForm()
    return render(request, "registration/registration.html", {"form": form})


def login_view(request):
    """Optional custom login view — safe to have, but project-level auth URLs may be used instead."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")  # send to dashboard which shows admin/general appropriately
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "registration/login.html")


def logout_view(request):
    auth_logout(request)
    return render(request, "registration/login.html")



@login_required
def dashboard(request):
    """
    Single entrypoint for /dashboard/
    Shows admin.html if user.is_superuser, otherwise general.html.
    """
    if request.user.is_superuser:
        return render(request, "dashboard/admin.html")
    return render(request, "dashboard/general.html")


@login_required
def general(request):
    """Direct route for /dashboard/general/"""
    return render(request, "dashboard/general.html")


@login_required
def admin_dashboard(request):
    """Direct route for /dashboard/admin-dashboard/"""
    return render(request, "dashboard/admin.html")
