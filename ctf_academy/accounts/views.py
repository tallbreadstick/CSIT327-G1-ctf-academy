# accounts/views.py

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

# --- ADDED IMPORTS FOR JWT AND API PROTECTION ---
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

# --- NEW VIEW TO GENERATE TOKEN WITH CUSTOM PAYLOAD ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# --- REMOVED THE OLD LoginView(APIView) CLASS ---
# The class above replaces it and handles token generation automatically.

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

# --- EXAMPLE OF A PROTECTED API ENDPOINT ---
# Any request to this view must include a valid JWT in the Authorization header.
# The library automatically rejects expired, tampered, or invalid tokens.
class ProtectedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is protected data, you are authenticated!'}
        return Response(content)

# ========== HTML PAGE VIEWS (Unchanged but with protection examples) ==========

def home_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_dashboard_page")
    return render(request, "accounts/home.html")

# To protect a page like 'about', you would add the @login_required decorator.
# If a logged-out user tries to visit /about, they will be sent to the /login page.
@login_required
def about_page(request):
    return render(request, "accounts/about.html")

def register_page(request):
    # This view remains unchanged
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

def login_page(request):
    # If user is already logged in, redirect them
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard_page")
        else:
            return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect without message
            if user.is_superuser:
                return redirect("admin_dashboard_page")
            else:
                return redirect("home")
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "accounts/login.html")
    
    # GET request - just show the form
    return render(request, "accounts/login.html")

def logout_page(request):
    logout(request)
    return render(request, "accounts/logout.html")

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard_page(request):
    return render(request, "accounts/admin_dashboard.html")