# Create your views here.

from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib import messages
# --- ADDED IMPORTS ---
from django.contrib.auth.decorators import login_required, user_passes_test


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        

# --- MODIFIED HOME PAGE VIEW ---
def home_page(request):
    # If a logged-in admin tries to visit the home page, send them to their dashboard
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_dashboard_page")
        
    return render(request, "accounts/home.html")


def about_page(request):
    return render(request, "accounts/about.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "accounts/register.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "accounts/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "accounts/register.html")

        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, "accounts/register.html")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! You can log in now.")
        return redirect("login_page")

    return render(request, "accounts/register.html")


# --- MODIFIED LOGIN PAGE VIEW ---
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            
            # --- THIS IS THE REDIRECTION LOGIC ---
            if user.is_superuser:
                return redirect("admin_dashboard_page")  # Go to admin dashboard
            else:
                return redirect("home")  # Go to regular home page
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "accounts/login.html")

    return render(request, "accounts/login.html")


def logout_page(request):
    logout(request)
    return render(request, "accounts/logout.html")

# --- HELPER FUNCTION and NEW VIEW FOR ADMIN DASHBOARD ---
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard_page(request):
    return render(request, "accounts/admin_dashboard.html")
